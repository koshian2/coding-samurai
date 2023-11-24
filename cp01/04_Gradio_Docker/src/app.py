import gradio as gr
from PIL import Image
import numpy as np

def generate_image(n_ninja, n_samurai):
    with Image.new("RGBA", (1024, 768), (255, 255, 255)) as canvas:
        with Image.open("ninja.png") as ninja:
            with Image.open("samurai.png") as samurai:
                # ninja.pngをn_ninja個、samurai.pngをn_samurai個配置
                indices = np.concatenate([np.full(int(n_ninja), 0), np.full(int(n_samurai), 1)])
                np.random.shuffle(indices)
                for ind in indices:
                    if ind == 0:
                        left = np.random.randint(0, canvas.width-ninja.width)
                        top = np.random.randint(0, canvas.height-ninja.height)
                        canvas.paste(ninja, (left, top), ninja)
                    else:
                        left = np.random.randint(0, canvas.width-samurai.width)
                        top = np.random.randint(0, canvas.height-samurai.height)
                        canvas.paste(samurai, (left, top), samurai)
        return canvas

with gr.Blocks() as demo:
    num_ninja = gr.Number(value=1, minimum=1, maximum=10, step=1, label="忍者")
    num_samurai = gr.Number(value=1, minimum=1, maximum=10, step=1, label="侍")

    button = gr.Button(value="曲者じゃ！出会え、出会え！")
    canvas = gr.Image()
    button.click(generate_image, [num_ninja, num_samurai], canvas)

if __name__ == "__main__":
    demo.launch(server_port=8080, server_name="0.0.0.0")