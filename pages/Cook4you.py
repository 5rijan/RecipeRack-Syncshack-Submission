openai_api_key = ""

import streamlit as st
from langchain.llms import OpenAI
import sqlite3

def get_pantry_items(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT item_name, quantity, unit FROM pantry WHERE username = ?', (username,))
    items = c.fetchall()
    conn.close()
    return items

def format_pantry_items(pantry_items):
    if pantry_items:
        return ', '.join([f"{item[0]} ({item[1]} units of {item[2]})" for item in pantry_items])
    return "No pantry items available."

# Function to format the query with detailed information
def create_query(title, calories, prep_time, use_pantry, pantry_list, use_pantry_message):
    if pantry_list:
        query = (
            f"I need a recipe for {title}. The recipe should approximately take {prep_time} minutes to prepare and should have around {calories} calories. "
            f"Use the following pantry items if possible: {pantry_list}. "
            f"Please follow these instructions precisely:\n"
            f"1. Provide the recipe title.\n"
            f"2. List all the ingredients needed, divided into two sections:\n"
            f"   - **From the pantry:** List only those ingredients that are available in the pantry. Ensure that the items from the pantry are correctly identified and do not include anything that is not available.\n"
            f"   - **To be bought:** List all ingredients that need to be purchased. Ensure that this list only includes items that are not in the pantry.\n"
            f"3. Provide detailed instructions for making the recipe.\n"
            f"\nDo not include any extraneous information. Ensure all details are accurate and adhere strictly to the instructions."
        )
    else:
        query = (
            f"I need a recipe for {title}. The recipe should approximately take {prep_time} minutes to prepare and should have around {calories} calories. "
            f"Please follow these instructions precisely:\n"
            f"1. Provide the recipe title.\n"
            f"2. List all the ingredients needed, divided into one section:\n"
            f"   - **To be bought:** List all ingredients that need to be purchased. Ensure that this list only includes items that are not in the pantry.\n"
            f"3. Provide detailed instructions for making the recipe.\n"
            f"\nDo not include any extraneous information. Ensure all details are accurate and adhere strictly to the instructions."
        )

    return query

def generate_response(input_text):
    llm = OpenAI(
        temperature=0.5, 
        openai_api_key=openai_api_key, 
        max_tokens=2048  
    )
    response = llm(input_text)
    
    if response:
        st.write(response) 
    else:
        st.error("No response received from the API.")

st.title("👨🏻‍🍳🍙 Your Own Chef")
default_calories = 300
default_prep_time = "30 minutes"

with st.form("my_form"):
    st.subheader("Recipe Request")
    
    title = st.text_area("Instructions", height=150, help="Describe the type of food or recipe you want.")
    calories = st.number_input("Calories (default: 300)", min_value=0, value=default_calories)
    prep_time = st.text_input("Preparation Time (default: 30 minutes)", value=default_prep_time)
    use_pantry = st.checkbox("Include pantry items")

    if use_pantry and not st.session_state.get('logged_in', False):
        st.warning("You need to sign in to use the pantry feature.")

    submitted = st.form_submit_button("Submit")

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
    elif submitted:
        if use_pantry:
            if st.session_state.get('logged_in', False):
                username = st.session_state.get('username')
                pantry_items = get_pantry_items(username)
                pantry_list = format_pantry_items(pantry_items)
                if pantry_items:
                    query = create_query(title, calories, prep_time, use_pantry, pantry_list, "")
                else:
                    query = create_query(title, calories, prep_time, use_pantry, "", "There is nothing in the pantry. Everything to be put in To be bought section")
            else:
                query = create_query(title, calories, prep_time, use_pantry, "", "There is nothing in the pantry. Everything to be put in To be bought section")
        else:
            query = create_query(title, calories, prep_time, use_pantry, "", "")
        st.warning("You need to sign in to use the include pantry feature.")
        generate_response(query)
