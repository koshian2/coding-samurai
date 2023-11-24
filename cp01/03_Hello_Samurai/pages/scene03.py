import streamlit as st

st.markdown("# 侍との対話")
st.image("imgs/scene03.jpg")

with st.chat_message("侍"):
    st.markdown("あなたの名前を教えてください")
with st.chat_message("user"):
    name = st.text_input("名前：")
    button = st.button("名を名乗る")
if button:
    with st.chat_message("侍"):
        st.markdown(f"{name}というのか、覚えておこう")
        st.session_state["name"] = name

    st.markdown("scene04に進んでください")