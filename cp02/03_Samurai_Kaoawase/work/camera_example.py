import gradio as gr
import datetime

def shot(image):
    print(datetime.datetime.now(), image.size, type(image))

with gr.Blocks() as demo:
    # Gradio Ver.3の場合
    # camera_image = gr.Image(type="pil", source="webcam", streaming=True, width=768, height=512)
    camera_image = gr.Image(type="pil", sources=["webcam"], streaming=True, width=768, height=512)
    button_shot = gr.Button("Shot")
    button_shot.click(shot, camera_image, None)

if __name__ == "__main__":
    demo.launch()
