import gradio as gr

def password_auth(username, password):
    return username == "admin" and password == "samurai1234"
    
with gr.Blocks() as demo:
    gr.Markdown("# Hello, samurai!")

if __name__ == "__main__":
    demo.launch(auth=password_auth)