import gradio as gr

_USERNAME = None

def login(username):
    global _USERNAME
    _USERNAME = username
    return f"{username}さんがログインしました！"

def greet():
    return f"{_USERNAME}さん、こんにちは！"

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            tb_username = gr.Textbox(label="Input your name")
            button_login = gr.Button(value="Login")
        with gr.Column():
            message = gr.Markdown()
            button_greet = gr.Button(value="Greet")

    button_login.click(login, tb_username, message)
    button_greet.click(greet, None, message)

if __name__ == "__main__":
    demo.launch()
