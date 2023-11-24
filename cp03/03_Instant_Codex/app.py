import streamlit as st
import logic
import asyncio
import streamlit.components.v1 as components

def main():
    if "lang" not in st.session_state.keys():
        logic.initialize_state()

    # Sidebar
    lang_select = st.sidebar.radio("Language", ["日本語", "English"],
                                   index=0 if st.session_state["lang"] == "jp" else 1)
    if lang_select == "日本語":
        st.session_state["lang"] = "jp"
    elif lang_select == "English":
        st.session_state["lang"] = "en"
    
    button_download = st.sidebar.button("Download Result")

    st.markdown("# 📖 InstantCodex 🏃‍♂️")
    paper_url = st.text_input(label="Put paper url", placeholder="https://arxiv.org/abs/1706.03762")
    button_sumamrize = st.button("Start Summarize")

    # Chat History
    chat_history = st.session_state["messages_en"] if st.session_state["lang"] == "en" else st.session_state["messages_jp"]
    for chat_item in chat_history:
        with st.chat_message(chat_item["role"]):
            st.markdown(chat_item["content"])

    if button_sumamrize:
        with st.spinner("Downloading PDF & Parsing ..."):
            asyncio.run(logic.run_summarize(paper_url))

    if button_download:
        download_link = logic.get_download_injection_html()
        components.html(download_link)

if __name__ == "__main__":
    main()