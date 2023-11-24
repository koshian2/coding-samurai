import onnxruntime
from decord import VideoLoader, cpu
import numpy as np
import moviepy.editor as mpe
from fastapi import FastAPI, Request
import tempfile
import uvicorn
import os

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"app_name": "edoflow-highlighter-backend"}

async def run_raft(video_path, window=60):
    model_path = "models/raft_things_iter20_480x640.onnx"
    session = onnxruntime.InferenceSession(model_path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])

    # get input/output names
    model_inputs = session.get_inputs()
    input_names = [model_inputs[i].name for i in range(len(model_inputs))]    
    model_outputs = session.get_outputs()
    output_names = [model_outputs[i].name for i in range(len(model_outputs))]
    input_shape = model_inputs[0].shape # (1, 3, 480, 640)

    # get fps
    fps = round(mpe.VideoFileClip(video_path).fps)

    loader = VideoLoader([video_path], ctx=cpu(0), 
                          shape=(1, input_shape[2], input_shape[3], 3), skip=fps-1, interval=0, shuffle=False)
    prev_frame = None
    raw_frame_nums, windowed_frame_nums = [], []
    raw_flow_scores, windowed_flow_scores = [], []

    for batch in loader:
        current_frame = batch[0].asnumpy().transpose(0, 3, 1, 2).astype(np.float32)
        if prev_frame is None:
            prev_frame = current_frame
            continue
        
        outputs = session.run(output_names, {
            input_names[0]: prev_frame, 
			input_names[1]: current_frame})
        prev_frame = current_frame
        flow_map = outputs[1][0].transpose(1, 2, 0)
        flow_norm = np.linalg.norm(flow_map, axis=-1)

        frame_index = int(batch[1].asnumpy()[0][1])
        raw_frame_nums.append(frame_index)
        raw_flow_scores.append(float(np.mean(flow_norm)))

    for i in range(len(raw_frame_nums)//window + 1):
        windowed_frame_nums.append(i)
        windowed_flow_scores.append(np.mean(raw_flow_scores[i*window:(i+1)*window]))

    result = {
        "raw_frame_nums": raw_frame_nums,
        "raw_flow_scores": raw_flow_scores,
        "windowed_frame_nums": windowed_frame_nums,
        "windowed_flow_scores": windowed_flow_scores,
        "fps": fps
    }
    return result

@app.post("/invocations")
async def main(request: Request):
    # write file
    fp = tempfile.NamedTemporaryFile(delete=False)
    fp.write(await request.body())
    fp.close()

    # run raft
    result = await run_raft(fp.name)
    os.remove(fp.name)
    return result

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080
    )