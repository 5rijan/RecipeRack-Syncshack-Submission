import streamlit as st
from streamlit_navigation_bar import st_navbar
from st_pages import hide_pages
from time import sleep

st.set_page_config(
    page_title="RecipeRack",
    page_icon=":guardsman:",  
    initial_sidebar_state="collapsed" 
)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def switch_to_login():
    st.session_state["logged_in"] = False
    st.error("You need to log in to access this page.")
    sleep(0.5)
    st.switch_page("pages/Pantry.py")


PAGES = {
    "Home": "Pages/Home.py",
    "Recipes": "Pages/Recipe.py",
    "Cook4you": "Pages/Cook4you.py",
    "Pantry": "Pages/Pantry.py",
}

page = st_navbar(list(PAGES.keys()), key="navbar_unique_key")

if page:
    if page == "Pantry" and not st.session_state["logged_in"]:
        switch_to_login()
    else:
        page_file = PAGES.get(page)
        if page_file:
            with open(page_file, "r") as f:
                exec(f.read()) 
