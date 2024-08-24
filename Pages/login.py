import streamlit as st
from time import sleep
from st_pages import hide_pages
from streamlit_navigation_bar import st_navbar
from st_pages import hide_pages

def log_in():
    st.session_state["logged_in"] = True
    hide_pages([]) 
    st.success("Logged in!")
    sleep(0.5)
    st.switch_page("Main.py")

if not st.session_state.get("logged_in", False):
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "test" and password == "test": 
            st.session_state["username"] = username 
            log_in()
        else:
            st.error("Incorrect username or password")
    if st.button("Sign Up"):
        st.switch_page("pages/signup.py")

else:
    st.success("Already logged in. Redirecting to your profile...")
    sleep(0.5)
    st.switch_page("Main.py")
