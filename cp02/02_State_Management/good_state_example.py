import gradio as gr

def login(username):
    return f"{username}さんがログインしました！", username

def greet(name_state):
    return f"{name_state}さん、こんにちは！"

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            tb_username = gr.Textbox(label="Input your name")
            button_login = gr.Button(value="Login")
        with gr.Column():
            message = gr.Markdown()
            button_greet = gr.Button(value="Greet")
    name_state = gr.State("")

    button_login.click(login, [tb_username], [message, name_state])
    button_greet.click(greet, [name_state], [message])

if __name__ == "__main__":
    demo.launch()
