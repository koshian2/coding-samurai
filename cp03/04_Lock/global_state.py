import streamlit as st
import uuid

@st.cache_resource
def get_global_id():
    return uuid.uuid4()

def get_session_id():
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = uuid.uuid4()
    return st.session_state["session_id"]

def main():
    button = st.button("Click Me")
    if button:
        st.write("Global ID", get_global_id())
        st.write("Session ID", get_session_id())

if __name__ == "__main__":
    main()