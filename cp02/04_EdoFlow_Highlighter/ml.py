import onnxruntime
from decord import VideoLoader, cpu
import numpy as np
from tqdm import tqdm
import moviepy.editor as mpe

def run_raft(video_path, window=60):
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

    for batch in tqdm(loader):
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

    return raw_frame_nums, raw_flow_scores, windowed_frame_nums, windowed_flow_scores, fps

