import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.base import BaseCallbackHandler
from typing import Any

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container: st.empty):
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self.text += token
        self.container.markdown(self.text)

def run_chain(question: str, container: st.empty):
    stream_callback = StreamHandler(container)
    llm = ChatOpenAI(model="gpt-3.5-turbo-0613", temperature=0.2, 
                     max_tokens=1024, streaming=True, callbacks=[stream_callback])
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("与えられた内容を現代日本語に訳してください"),
        HumanMessagePromptTemplate.from_template("{human_input}")
    ])
    chain = LLMChain(llm=llm, prompt=prompt_template, callbacks=[stream_callback])
    answer = chain.run(human_input=question)
    # add to state
    st.session_state["messages"] += [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer}
    ]

def main():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    st.markdown("# 📜ZenVox🎎")
    st.markdown("Translates Japanese archaic text into modern Japanese. ")
    st.markdown("💬 Chat with me")
    # Chat history
    for item in st.session_state["messages"]:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])

    chat_input = st.chat_input("Input your message")
    if chat_input:
        with st.chat_message("user"):
            st.markdown(chat_input)
        with st.chat_message("assistant"):
            container = st.empty()
        run_chain(chat_input, container)

if __name__ == "__main__":
    main()