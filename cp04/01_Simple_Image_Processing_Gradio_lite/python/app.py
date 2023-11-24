import gradio as gr
from PIL import Image, ImageFilter
import numpy as np

def blur_image(img_array):
    with Image.fromarray(img_array) as img:
        blur_img = img.filter(ImageFilter.GaussianBlur(radius=5))
        return np.array(blur_img)

with gr.Blocks() as block:
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(label="Your Image", type="numpy")
            button_flip_horizontal = gr.Button("Flip Horizontal")
            button_flip_vertical = gr.Button("Flip Vertical")
            button_blur_image = gr.Button("Blur Image")
        with gr.Column():
            output_image = gr.Image(label="Output Image", type="numpy", interactive=False)

    button_flip_horizontal.click(lambda x: x[:, ::-1, :], input_image, output_image)
    button_flip_vertical.click(lambda x: x[::-1, :, :], input_image, output_image)
    button_blur_image.click(blur_image, input_image, output_image)

if __name__ == "__main__":
    block.launch()