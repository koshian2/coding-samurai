import gradio as gr

def greet():
    return "Hello, Young Warrior"

with gr.Blocks() as demo:
    button = gr.Button("Welcome to Dojo")
    text = gr.Markdown()
    button.click(greet, None, text)

if __name__ == "__main__":
    demo.launch()
