import streamlit as st

if not "name" in st.session_state:
    st.session_state["name"] = ""

st.markdown("# さようなら")
st.image("imgs/scene04.jpg")

with st.chat_message("侍"):
    st.markdown(f"また会う日を楽しみにしている、{st.session_state['name']}")
with st.chat_message("user"):
    button = st.button("さようなら")
    if button:
        st.markdown(f"さようなら")

if button:
    st.markdown("おわり。scene01に戻ってください")