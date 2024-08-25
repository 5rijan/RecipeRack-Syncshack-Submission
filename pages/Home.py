import streamlit as st
import sqlite3
from datetime import datetime
from PIL import Image
from io import BytesIO

# Function to create the recipes table with a 'likes' column
def create_recipes_table():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS Recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            date_submitted TEXT,
            title TEXT,
            instructions TEXT,
            calories INTEGER,
            serves INTEGER,
            image BLOB,
            likes INTEGER DEFAULT 0  -- Add a likes column with default value 0
        )
    ''')
    conn.commit()
    conn.close()

# Function to create the comments table
def create_comments_table():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS Comments (
            comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            username TEXT,
            comment TEXT,
            date_commented TEXT,
            FOREIGN KEY (recipe_id) REFERENCES Recipes(id)
        )
    ''')
    conn.commit()
    conn.close()

create_recipes_table()
create_comments_table()

st.sidebar.title("Post Recipes")

if st.session_state.get('logged_in', False):
    st.sidebar.markdown(f"## **Hi {st.session_state.get('username')}** Welcome Back!")

    with st.sidebar.form("post_recipe_form"):
        st.subheader("Submit Your Recipe")

        title = st.text_input("Title")
        instructions = st.text_area("Instructions", height=200)
        calories = st.number_input("Calories", min_value=0, value=300)
        serves = st.number_input("Serves", min_value=1, value=1)
        uploaded_image = st.file_uploader("Upload Recipe Image", type=['jpg', 'jpeg', 'png'])

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            username = st.session_state.get('username')
            date_submitted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            image_data = uploaded_image.read() if uploaded_image else None

            conn = sqlite3.connect('recipes.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO Recipes (username, date_submitted, title, instructions, calories, serves, image)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, date_submitted, title, instructions, calories, serves, image_data))
            conn.commit()
            conn.close()

            st.success("Recipe submitted successfully!")
else:
    st.sidebar.write("You need to be logged in to post a recipe.")
    if st.sidebar.button("Log in"):
        st.switch_page("pages/login.py")

def display_recipes():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()

    # Select all recipes and their likes
    c.execute('''
        SELECT id, username, date_submitted, title, instructions, image, likes FROM Recipes
    ''')
    recipes = c.fetchall()
    conn.close()

    st.title("Recipe Gallery 🥪🏅")

    num_columns = 2
    cols = st.columns(num_columns)  

    for i, recipe in enumerate(recipes):
        recipe_id, username, date_submitted, title, instructions, photo_data, likes = recipe
        
        col = cols[i % num_columns]

        with col:
            # Create a styled container for each recipe with border, padding, and margin
            st.markdown(
                f"""
                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #f9f9f9;">
                    <h3 style="color: #333;">{title}</h3>
                    <p style="color: #333;">
                        <strong>Posted by:</strong> {username} &nbsp;|&nbsp; 
                        <strong>Date:</strong> {date_submitted}
                    </p>
                """,
                unsafe_allow_html=True
            )

            if photo_data:
                image = Image.open(BytesIO(photo_data))
                st.image(image, caption="Recipe Image", use_column_width=True)

            st.markdown(
                f"""
                <div style="max-height: 100px; overflow-y: hidden; text-overflow: ellipsis; margin-bottom: 10px; color: #555;">
                    {instructions[:150]}... <!-- Display only the first 150 characters -->
                </div>
                """,
                unsafe_allow_html=True
            )

            if len(instructions) > 150:
                with st.expander("Read More"):
                    st.write(instructions)

                    # Add the like button inside the expander
                    if st.button(f"Like ({likes})", key=f"like_button_{recipe_id}"):
                        # Increment like count in the database
                        conn = sqlite3.connect('recipes.db')
                        c = conn.cursor()
                        c.execute('''
                            UPDATE Recipes SET likes = likes + 1 WHERE id = ?
                        ''', (recipe_id,))
                        conn.commit()
                        conn.close()
                        st.rerun()  

                    st.write("### Comments")
                    display_comments(recipe_id)

                    # Comment input form
                    with st.form(key=f"comment_form_{recipe_id}"):
                        comment_name = st.text_input("Name")
                        comment_text = st.text_area("Comment", height=100)
                        submit_comment = st.form_submit_button("Submit Comment")

                        if submit_comment:
                            date_commented = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            conn = sqlite3.connect('recipes.db')
                            c = conn.cursor()
                            c.execute('''
                                INSERT INTO Comments (recipe_id, username, comment, date_commented)
                                VALUES (?, ?, ?, ?)
                            ''', (recipe_id, comment_name, comment_text, date_commented))
                            conn.commit()
                            conn.close()
                            st.success("Comment submitted successfully!")
                            st.rerun()  # Refresh to show updated comments

            st.markdown("</div>", unsafe_allow_html=True)

def display_comments(recipe_id):
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('''
        SELECT username, comment, date_commented FROM Comments WHERE recipe_id = ?
    ''', (recipe_id,))
    comments = c.fetchall()
    conn.close()

    if comments:
        for comment in comments:
            username, comment_text, date_commented = comment
            st.markdown(f"**{username}** on {date_commented}: {comment_text}")
    else:
        st.write("No comments yet. Be the first to comment!")

display_recipes()
