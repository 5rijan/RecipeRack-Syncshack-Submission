import streamlit as st
from time import sleep


def log_out():
    st.session_state["logged_in"] = False
    st.success("Logged out!")
    sleep(0.5)

if not st.session_state.get("logged_in", False):
    st.switch_page("pages/login.py")

else:
    st.title("Profile Page")
    st.write(f"Welcome back, {st.session_state.get('username', 'User')}!")
    if st.button("Log out"):
        log_out()
