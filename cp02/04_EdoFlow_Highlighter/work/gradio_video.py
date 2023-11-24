import gradio as gr

def play():
    return "video/暴れん坊将軍のテーマ [nBXX-RT38uQ].mp4"

with gr.Blocks() as demo:
    video = gr.Video()
    button = gr.Button("Play Video")
    button.click(play, inputs=None, outputs=video)

if __name__ == "__main__":
    demo.launch()