import torch
import open_clip
import gradio as gr
import plotly.express as px
import numpy as np

models = None

def get_models():
    global models
    if models is None:
        model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-16-SigLIP", pretrained="webli")
        tokenizer = open_clip.get_tokenizer("ViT-B-16-SigLIP")
        models = (model, preprocess, tokenizer)
    return models

def run_clip(input_image, input_prompt):
    # Preprocess
    model, preprocess, tokenizer = get_models()
    img = preprocess(input_image).unsqueeze(0)
    prompt = [x.strip() for x in input_prompt.split(",")]
    text = tokenizer(prompt)

    # Run CLIP
    with torch.no_grad():
        image_features = model.encode_image(img)
        text_features = model.encode_text(text)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1).numpy()[0]
    
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
    demo.launch()