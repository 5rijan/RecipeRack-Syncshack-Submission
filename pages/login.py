import streamlit as st
import sqlite3
from time import sleep
from streamlit_navigation_bar import st_navbar
from st_pages import hide_pages
import hashlib

def create_connection():
    conn = sqlite3.connect('users.db')
    return conn

# Function to hash passwords for comparison
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    conn = create_connection()
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user

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

    login_col, signup_col = st.columns([1, 2])
    
    with login_col:
        if st.button("Login"):
            user = verify_user(username, password)
            if user:
                st.session_state["username"] = username
                log_in()
            else:
                st.error("Incorrect username or password")

    with signup_col:
        if st.button("Don't have an account! Signup"):
            st.switch_page("pages/signup.py")
            
    
else:
    st.success("Already logged in. Redirecting to your profile...")
    sleep(0.5)
    st.switch_page("Main.py")
