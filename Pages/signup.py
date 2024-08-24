# signup.py
import streamlit as st
from PIL import Image

if "user_data" not in st.session_state:
    st.session_state.user_data = {}

def register_user(first_name, last_name, username, password, confirm_password, image=None):
    if username in st.session_state.user_data:
        st.error("Username already exists. Please choose a different one.")
    elif password != confirm_password:
        st.error("Passwords do not match. Please try again.")
    else:
        st.session_state.user_data[username] = {
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
            "image": image
        }
        st.success("Registration successful! Please log in.")
        st.switch_page("pages/login.py")


st.title("Sign Up")

first_name = st.text_input("First Name")
last_name = st.text_input("Last Name")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")
image = st.file_uploader("Upload Profile Image", type=["jpg", "jpeg", "png"])

if st.button("Register"):
    image_data = None
    if image is not None:
        image_data = Image.open(image)
    register_user(first_name, last_name, username, password, confirm_password, image_data)
