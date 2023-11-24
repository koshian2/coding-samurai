import open_clip
import torch
import gradio as gr
import time

def get_models(state):
    if state["models"] is None:
        model, _, preprocess = open_clip.create_model_and_transforms("ViT-bigG-14", pretrained="laion2b_s39b_b160k")
        tokenizer = open_clip.get_tokenizer("ViT-bigG-14")
        state["models"] = (model, preprocess, tokenizer)
    return state["models"]

def eval(state):
    start_time = time.time()
    model, preprocess, tokenizer = get_models(state)
    # Dummy evaluation
    text = tokenizer(["cat", "dog"])
    with torch.no_grad():
        text_features = model.encode_text(text)
    elapsed_time = time.time() - start_time
    return f"Done! Elapsed: {elapsed_time:.01f}s", state

with gr.Blocks() as demo:
    gr.Markdown("This demo loads a large model and evaluates it on CPU with Session State.")
    button = gr.Button("Evaluate")
    message = gr.Markdown()
    state = gr.State({"models": None})
    button.click(eval, state, [message, state])

if __name__ == "__main__":
    demo.launch()