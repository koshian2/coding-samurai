import streamlit as st

def check_password():
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    username = st.text_input("User Name")
    password = st.text_input("Password", type="password")
    button = st.button("Login")

    # Validation
    if button:
        if username == "admin" and password == "samurai1234":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

        if "password_correct" in st.session_state:
            if not st.session_state["password_correct"]:
                st.error("😕 Password incorrect")
                return False
            else:
                st.rerun()
    return False

def main():
    if not check_password():
        st.stop()  # Do not continue if check_password is not True.

    # Main Streamlit app starts here
    st.markdown("# Hello, Samurai")

if __name__ == "__main__":
    main()