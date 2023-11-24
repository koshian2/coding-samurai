import gradio as gr
import plotly.express as px
import numpy as np
import base64
import requests
import io
import json
import os
import boto3

def run_clip(input_image, input_prompt):
    with io.BytesIO() as buf:
        max_size = 1024
        # resize image not to too large
        if input_image.width > max_size or input_image.height > max_size:
            if input_image.width > input_image.height:
                ratio = input_image.width / input_image.height
                new_size = (max_size, int(max_size / ratio))
            else:
                ratio = input_image.height / input_image.width
                new_size = (int(max_size / ratio), max_size)
            input_image = input_image.resize(new_size)
        # convert to b64-string
        input_image.save(buf, format="JPEG", quality=92)
        buf.seek(0)
        base64_str = base64.b64encode(buf.getvalue()).decode()

    payload = {
        "image": base64_str,
        "prompt": input_prompt
    }

    if "RUN_ENV" not in os.environ.keys() or os.environ["RUN_ENV"] == "host":
        response = requests.post("http://127.0.0.1:9001/2015-03-31/functions/function/invocations", 
                                data=json.dumps(payload).encode("utf-8"))
        response = response.text
    elif os.environ["RUN_ENV"] == "docker":
        response = requests.post("http://host.docker.internal:9001/2015-03-31/functions/function/invocations", 
                                data=json.dumps(payload).encode("utf-8"))
        response = response.text
    else:
        lambda_client = boto3.client("lambda")
        response = lambda_client.invoke(FunctionName="EquipInsightBackend",
                                        Payload=json.dumps(payload).encode("utf-8"))
        response = response["Payload"].read().decode()
    text_probs = json.loads(response)
    prompt = [x.strip() for x in input_prompt.split(",")]

    # Plot Result
    fig = px.bar(x=prompt, y=text_probs, labels={"x":"Equipment", "y":"Prob"})
    idx = np.argmax(text_probs)
    text = f"# Your gear is \"{prompt[idx]}\" ({text_probs[idx]:.1%})"
    return fig, text

with gr.Blocks() as demo:
    gr.Markdown("<h1><center>🏯 Sengoku Equip Insight ⚔️🛡️</center></h1>")
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(type="pil")
            input_prompt = gr.Textbox(label="Prompt")
            button = gr.Button("🔍 Identify My Gear", variant="primary")
        with gr.Column():
            output_plot = gr.Plot()
            output_text = gr.Markdown()
    button.click(run_clip, [input_image, input_prompt], [output_plot, output_text])
    # gradio examples
    gr.Examples([
        ["imgs/DP368606.jpg", "a sword, a shield, an armor, a helmet"],
        ["imgs/DT305406.jpg", "a sword, a shield, an armor, a helmet"],
        ["imgs/DT306017.jpg", "a sword, a shield, an armor, a helmet"],
        ["imgs/dalle01.png", "a sword, a shield, an armor, a helmet"],
        ["imgs/38.25.34_001apr2014.jpg", "a sword, a sword guard"],
        ["imgs/38.25.34_001apr2014.jpg", "an insect, a dragon, a flower, a snake"]
    ], [input_image, input_prompt])

if __name__ == "__main__":
    if "RUN_ENV" not in os.environ.keys() or os.environ["RUN_ENV"] == "host":
        demo.launch()
    else:
        demo.launch(server_name="0.0.0.0", server_port=8080)