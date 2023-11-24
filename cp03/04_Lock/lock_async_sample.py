import streamlit as st
import threading
import uuid
import asyncio

@st.cache_resource
def get_lock_object():
    return threading.Lock()

async def heavy_process_async():
    print("Start", st.session_state["session_id"])
    await asyncio.sleep(10)
    print("End", st.session_state["session_id"])
    st.success("Done !")

def main():
    if "session_id" not in st.session_state.keys():
        st.session_state["session_id"] = uuid.uuid4()

    button = st.button("Click")
    if button:
        with get_lock_object():
            asyncio.run(heavy_process_async())

if __name__ == "__main__":
    main()