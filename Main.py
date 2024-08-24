import streamlit as st
from streamlit_navigation_bar import st_navbar

st.set_page_config(
    page_title="Bablufoods",
    page_icon=":guardsman:",  
    initial_sidebar_state="collapsed" 
)

PAGES = {
    "Home": "Pages/Home.py",
    "Recipes": "Pages/Recipes.py",
    "Cook4you": "Pages/Cook4you.py",
    "Profile": "Pages/Profile.py",
    "About": "Pages/About.py"
}

page = st_navbar(list(PAGES.keys()), key="navbar_unique_key")

if page:
    page_file = PAGES.get(page)
    if page_file:
        with open(page_file, "r") as f:
            exec(f.read())
