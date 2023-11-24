import streamlit as st

st.markdown("# 城門前")
st.image("imgs/scene01.jpg")

button = st.button("城内に入る")
if button:
    st.markdown("scene02に進んでください")