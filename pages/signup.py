import streamlit as st
import sqlite3
from PIL import Image
import hashlib

def create_connection():
    conn = sqlite3.connect('users.db')
    return conn

def create_users_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT UNIQUE,
                    password TEXT,
                    image BLOB)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(first_name, last_name, username, password, confirm_password, image=None):
    conn = create_connection()
    c = conn.cursor()

    if password != confirm_password:
        st.error("Passwords do not match. Please try again.")
        return

    hashed_password = hash_password(password)

    try:
        c.execute('INSERT INTO users (first_name, last_name, username, password, image) VALUES (?, ?, ?, ?, ?)',
                  (first_name, last_name, username, hashed_password, image))
        conn.commit()
        st.success("Registration successful! Please log in.")
        st.session_state["user_logged_in"] = True
        st.switch_page("pages/login.py")

    except sqlite3.IntegrityError:
        st.error("Username already exists. Please choose a different one.")
    finally:
        conn.close()

create_users_table()

st.title("Sign Up")

first_name = st.text_input("First Name")
last_name = st.text_input("Last Name")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")
image = st.file_uploader("Upload Profile Image", type=["jpg", "jpeg", "png"])

image_data = None
if image is not None:
    image_data = image.read()

if st.button("Register"):
    register_user(first_name, last_name, username, password, confirm_password, image_data)
