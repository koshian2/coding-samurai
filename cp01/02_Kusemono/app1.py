import gradio as gr

def gather(n_ninja, n_samurai):
    return f"# 忍者{int(n_ninja)}人、侍{int(n_samurai)}人、合計{int(n_ninja+n_samurai)}人が駆けつけました"

with gr.Blocks() as demo:
    num_ninja = gr.Number(value=1, minimum=1, maximum=10, step=1, label="忍者")
    num_samurai = gr.Number(value=1, minimum=1, maximum=10, step=1, label="侍")

    button = gr.Button(value="曲者じゃ！出会え、出会え！")
    text = gr.Markdown()
    button.click(gather, [num_ninja, num_samurai], text)

if __name__ == "__main__":
    demo.launch()
