import streamlit as st
import sqlite3
from PIL import Image
from io import BytesIO
from time import sleep
import pandas as pd
from datetime import datetime

def create_connection():
    conn = sqlite3.connect('users.db')
    return conn

def fetch_user_details(username):
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT first_name, last_name, username, image FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def create_pantry_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pantry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    item_name TEXT,
                    quantity INTEGER,
                    unit TEXT,
                    expiration_date DATE,
                    notes TEXT,
                    added_date DATE,
                    FOREIGN KEY (username) REFERENCES users (username))''')
    conn.commit()
    conn.close()

def create_pantry_history_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pantry_history (
                    id INTEGER,
                    username TEXT,
                    item_name TEXT,
                    quantity INTEGER,
                    unit TEXT,
                    expiration_date DATE,
                    notes TEXT,
                    added_date DATE,
                    modified_date DATE,
                    FOREIGN KEY (id) REFERENCES pantry (id))''')
    conn.commit()
    conn.close()

def add_pantry_item(username, item_name, quantity, unit, expiration_date, notes):
    conn = create_connection()
    c = conn.cursor()
    added_date = datetime.now().strftime('%Y-%m-%d')  # Current date in YYYY-MM-DD format
    c.execute('INSERT INTO pantry (username, item_name, quantity, unit, expiration_date, notes, added_date) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (username, item_name, quantity, unit, expiration_date, notes, added_date))
    conn.commit()
    conn.close()

def update_pantry_item(item_id, item_name, quantity, unit, expiration_date, notes):
    conn = create_connection()
    c = conn.cursor()
    
    modified_date = datetime.now().strftime('%Y-%m-%d')
    
    c.execute('UPDATE pantry SET item_name = ?, quantity = ?, unit = ?, expiration_date = ?, notes = ?, added_date = ? WHERE id = ?',
              (item_name, quantity, unit, expiration_date, notes, modified_date, item_id))
    
    # Insert a new record into the pantry_history table
    c.execute('INSERT INTO pantry_history (id, item_name, quantity, unit, expiration_date, notes, added_date, modified_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
              (item_id, item_name, quantity, unit, expiration_date, notes, modified_date, modified_date))
    
    conn.commit()
    conn.close()

def delete_pantry_item(item_id):
    conn = create_connection()
    c = conn.cursor()
    
    # Delete the item from the pantry table
    c.execute('DELETE FROM pantry WHERE id = ?', (item_id,))
    
    # Also delete related history entries
    c.execute('DELETE FROM pantry_history WHERE id = ?', (item_id,))
    
    conn.commit()
    conn.close()

def fetch_pantry_items(username):
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT id, item_name, quantity, unit, expiration_date, notes, added_date FROM pantry WHERE username = ? ORDER BY added_date DESC', (username,))
    items = c.fetchall()
    conn.close()
    return items

def fetch_pantry_history(item_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM pantry_history WHERE id = ? ORDER BY modified_date DESC', (item_id,))
    history = c.fetchall()
    conn.close()
    return history

def log_out():
    st.session_state["logged_in"] = False
    st.success("Logged out!")
    sleep(0.5)
    st.switch_page("pages/login.py")

create_pantry_table()
create_pantry_history_table()

if not st.session_state.get("logged_in", False):
    st.switch_page("pages/login.py")
else:
    username = st.session_state.get('username')
    user_details = fetch_user_details(username)

    if user_details:
        first_name, last_name, username, image_data = user_details
        st.title(f"Welcome back, **{first_name} {last_name}**!")
        if image_data:
            try:
                if isinstance(image_data, bytes):
                    st.image(BytesIO(image_data), caption=f"{first_name}'s Profile Picture", width=150)
                else:
                    st.error("Image data is not in bytes format.")
            except Exception as e:
                st.error(f"Error loading image: {e}")
        st.header("Pantry Management")

        with st.form("add_item_form"):
            st.subheader("Add New Pantry Item")
            item_name = st.text_input("Item Name")
            quantity = st.number_input("Quantity", min_value=1)
            unit = st.text_input("Unit")
            expiration_date = st.date_input("Expiration Date")
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Add Item")

            if submitted:
                add_pantry_item(username, item_name, quantity, unit, expiration_date, notes)
                st.success("Item added successfully!")

        st.subheader("Your Pantry Items")
        pantry_items = fetch_pantry_items(username)
        if pantry_items:
            # Convert pantry items to DataFrame
            df = pd.DataFrame(pantry_items, columns=["ID", "Item Name", "Quantity", "Unit", "Expiration Date", "Notes", "Added Date"])
            st.write(f"**Total Items:** {len(pantry_items)}")
            st.dataframe(df)
            selected_item_id = st.selectbox("Select an item to view stats", df["ID"])

            if selected_item_id:
                history = fetch_pantry_history(selected_item_id)
                if history:
                    history_df = pd.DataFrame(history, columns=["ID", "Username", "Item Name", "Quantity", "Unit", "Expiration Date", "Notes", "Added Date", "Modified Date"])
                    history_df['Unit'] = pd.to_numeric(history_df['Unit'], errors='coerce').fillna(1)
                    history_df['Total Consumption'] = history_df['Quantity'] * history_df['Unit']
                    history_df['Modified Date'] = pd.to_datetime(history_df['Modified Date'])

                    # Plot Total Consumption
                    st.line_chart(data=history_df.set_index('Modified Date')['Total Consumption'], use_container_width=True)


            # Edit Pantry Button
            st.subheader("Edit Pantry Item")
            with st.form("edit_item_form"):
                item_id = st.number_input("Item ID to Edit", min_value=1, format="%d")
                item_name_to_edit = st.text_input("Item Name (optional)")
                edit_submitted = st.form_submit_button("Edit Pantry Item")

                if edit_submitted:
                    item = next((i for i in pantry_items if i[0] == item_id), None)
                    if item:
                        st.session_state["editing_item"] = item
                        st.session_state["editing_item_id"] = item_id
                    else:
                        st.error("Item ID not found.")

            if "editing_item" in st.session_state:
                item = st.session_state["editing_item"]
                item_id = st.session_state["editing_item_id"]
                st.subheader(f"Edit Item: {item[1]}")
                
                with st.form(f"edit_item_form_{item_id}"):
                    new_item_name = st.text_input("Item Name", value=item[1])
                    new_quantity = st.number_input("Quantity", min_value=1, value=item[2])
                    new_unit = st.text_input("Unit", value=item[3])
                    new_expiration_date = st.date_input("Expiration Date")
                    new_notes = st.text_area("Notes", value=item[5])
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        update_submitted = st.form_submit_button("Update Item")

                    with col2:
                        delete_submitted = st.form_submit_button("Delete Item")

                    if update_submitted:
                        update_pantry_item(item_id, new_item_name, new_quantity, new_unit, new_expiration_date, new_notes)
                        st.success("Item updated successfully!")
                        st.rerun()

                    if delete_submitted:
                        delete_pantry_item(item_id)
                        st.success("Item deleted successfully!")
                        st.rerun()
                
        else:
            st.write("No items found in your pantry.")

        if st.button("Edit Profile"):
            st.switch_page("pages/Edit.py")

        if st.button("Log out"):
            log_out()
    else:
        st.error("Error fetching user details. Please log in again.")
        st.button("Log out", on_click=log_out)
