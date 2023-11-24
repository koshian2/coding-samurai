import gradio as gr
from PIL import Image
import numpy as np

animation_state = []

def initialize_animation(n_ninja, n_samurai):
    ninja_size = Image.open("ninja.png").size
    samurai_size = Image.open("samurai.png").size
    global animation_state
    animation_state = []

    for i in range(int(n_ninja)):
        left = np.random.randint(0, 1024-ninja_size[0])
        top = np.random.randint(0, 768-ninja_size[1])
        animation_state.append({
            "person": "ninja",
            "left": left,
            "top": top,
            "show": False
        })
    for i in range(int(n_samurai)):
        left = np.random.randint(0, 1024-samurai_size[0])
        top = np.random.randint(0, 768-samurai_size[1])
        animation_state.append({
            "person": "samurai",
            "left": left,
            "top": top,
            "show": False
        })
    np.random.shuffle(animation_state)

def drawer(canvas):
    if len(animation_state) == 0:
        return canvas

    current_idx = sum([animation_state[i]["show"] for i in range(len(animation_state))])
    if current_idx < len(animation_state):
        animation_state[current_idx]["show"] = True

    with Image.new("RGBA", (1024, 768), (255, 255, 255)) as img:
        for i in range(len(animation_state)):
            with Image.open("ninja.png") as ninja:
                with Image.open("samurai.png") as samurai:

                    item = animation_state[i]
                    if item["show"]:
                        target_img = ninja if item["person"] == "ninja" else samurai
                        img.paste(target_img, (item["left"], item["top"]), target_img)
        return img

with gr.Blocks() as demo:
    num_ninja = gr.Number(value=1, minimum=1, maximum=10, step=1, label="忍者")
    num_samurai = gr.Number(value=1, minimum=1, maximum=10, step=1, label="侍")

    button = gr.Button(value="曲者じゃ！出会え、出会え！")
    canvas = gr.Image(width=1024, height=768, interactive=False)
    button.click(initialize_animation, [num_ninja, num_samurai], None).then(
        drawer, canvas, canvas, every=1)

if __name__ == "__main__":
    demo.queue().launch()
