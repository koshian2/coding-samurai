import streamlit as st
import threading
import torch
@st.cache_resource
def get_lock_object():
    return threading.Lock()

@st.cache_resource
def load_model():
    from transformers import AutoTokenizer, AutoModelForCausalLM
    model_name = "stabilityai/japanese-stablelm-instruct-beta-7b"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    # The next line may need to be modified depending on the environment
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, 
                                                 low_cpu_mem_usage=True, device_map="cuda")
    return model, tokenizer

def generate(system_str: str, question_str: str):
    with get_lock_object():
        model, tokenizer = load_model()
    system_message = {"role": "system", "content": system_str}
    question_message = {"role": "user", "content": question_str}
    chat_message = [system_message] + st.session_state["messages"] + [question_message]
    # prompt = tokenizer.apply_chat_template(chat_message, tokenize=False).replace("<</SYS>>", "<<SYS>>")
    prompt = tokenizer.apply_chat_template(chat_message, tokenize=False)
    print(prompt)

    with torch.no_grad():
        input_ids = tokenizer.encode(
            prompt,
            add_special_tokens=False,
            return_tensors="pt"
        )

        with get_lock_object():
            tokens = model.generate(
                input_ids.to(device=model.device),
                max_new_tokens=128,
                temperature=1.0,
                top_p=0.95,
                do_sample=True
            )

    out = tokenizer.decode(tokens[0][input_ids.size(1):], skip_special_tokens=True)
    st.session_state["messages"].append(question_message)
    st.session_state["messages"].append({"role": "assistant", "content": out})
    return out

def main():
    if not "messages" in st.session_state.keys():
        st.session_state["messages"] = []
        st.session_state.input = ""

    st.markdown("# Japanese-StableLM-Beta")
    system_input = st.text_input("System Prompt", "あなたは役立つアシスタントです")
    chat_input = st.chat_input("User Message")

    for item in st.session_state["messages"]:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
    if chat_input:
        with st.chat_message("user"):
            st.markdown(chat_input)
        answer = generate(system_input, chat_input)
        with st.chat_message("assistant"):
            st.markdown(answer)

if __name__ == "__main__":
    main()
