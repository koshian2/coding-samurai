import streamlit as st

st.markdown("# 場内の広場")
st.image("imgs/scene02.jpg")

with st.chat_message("侍"):
    st.markdown("こんにちは、旅人。我々の土地にようこそ。")
with st.chat_message("user"):
    button = st.button("挨拶を返す")

if button:
    with st.chat_message("侍"):
        st.markdown("礼儀正しい旅人だ")

    st.markdown("scene03に進んでください")