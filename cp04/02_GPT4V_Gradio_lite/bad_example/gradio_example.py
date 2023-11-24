import openai
import gradio as gr
import os
import base64

def chat(user_question, chat_history, upload_image, api_token, state):
    client = openai.OpenAI(api_key=api_token)

    user_content = []
    user_content.append({"type": "text", "text": user_question})
    if upload_image is not None:
        with open(upload_image, "rb") as fp:
            base64_image = base64.b64encode(fp.read()).decode("utf-8")
            ext = os.path.splitext(upload_image)[1].replace(".", "")
        user_content.append({"type": "image_url", "image_url": f"data:image/{ext};base64,{base64_image}"})
    state["messages"].append({
        "role": "user",
        "content": user_content,
    })
 
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=state["messages"],
        max_tokens=512,
    )
    response = response.choices[0].message.content

    state["messages"].append({
        "role": "assistant",
        "content": [
            {"type": "text", "text": response}
        ]
    })

    if upload_image is not None:
        chat_history.append((user_question, None))
        chat_history.append(((upload_image,), response))
    else:
        chat_history.append((user_question, response))
    return "", chat_history, None, state

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            upload_image = gr.Image(type="filepath")
            api_token = gr.Textbox(label="OpenAI API Key", placeholder="Your OpenAI API Key", type="password")
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(height=1024)
    with gr.Row():
        msg = gr.Textbox(label="Input text", placeholder="Your message here")

    state = gr.State({"messages": []})
    msg.submit(chat, [msg, chatbot, upload_image, api_token, state], [msg, chatbot, upload_image, state])

if __name__ == "__main__":
    demo.launch()