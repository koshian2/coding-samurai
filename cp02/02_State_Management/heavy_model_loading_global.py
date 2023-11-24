import open_clip
import torch
import gradio as gr
import time

models = None

def get_models():
    global models
    if models is None:
        model, _, preprocess = open_clip.create_model_and_transforms("ViT-bigG-14", pretrained="laion2b_s39b_b160k")
        tokenizer = open_clip.get_tokenizer("ViT-bigG-14")
        models = (model, preprocess, tokenizer)
    return models

def eval():
    start_time = time.time()
    model, preprocess, tokenizer = get_models()
    # Dummy evaluation
    text = tokenizer(["cat", "dog"])
    with torch.no_grad():
        text_features = model.encode_text(text)
    elapsed_time = time.time() - start_time
    return f"Done! Elapsed: {elapsed_time:.01f}s"

with gr.Blocks() as demo:
    gr.Markdown("This demo loads a large model and evaluates it on CPU with Global State.")
    button = gr.Button("Evaluate")
    message = gr.Markdown()
    button.click(eval, None, message)

if __name__ == "__main__":
    demo.launch()