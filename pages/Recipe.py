import streamlit as st
import requests
import random

# Define API endpoint and key
API_URL_SEARCH = "https://api.spoonacular.com/recipes/complexSearch"
API_URL_DETAIL = "https://api.spoonacular.com/recipes/{id}/information"
API_KEY = ""

def fetch_recipes(query):
    params = {
        "query": query,
        "number": 10,  
        "apiKey": API_KEY
    }
    response = requests.get(API_URL_SEARCH, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        st.error("Failed to fetch recipes.")
        return []

def fetch_recipe_details(recipe_id):
    url = API_URL_DETAIL.format(id=recipe_id)
    params = {"apiKey": API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch details for recipe ID {recipe_id}.")
        return {}

def generate_recipe_text(recipe, details):
    """Generate a text representation of the recipe."""
    ingredients = ', '.join([ingredient['name'] for ingredient in details.get('extendedIngredients', [])])
    instructions = details.get('instructions', 'No instructions available.')
    return f"**{details['title']}**\n\n" \
           f"**Ingredients:** {ingredients}\n\n" \
           f"**Instructions:** {instructions}\n\n" \
           f"**Source:** {details['sourceUrl']}"

def display_recipe(recipe):
    """Display recipe details in a box."""
    recipe_id = recipe['id']
    details = fetch_recipe_details(recipe_id)
    
    if details:
        st.write(f"**{details['title']}**")
        st.image(details['image'], use_column_width=True)
        st.write(f"**Ingredients:** {', '.join([ingredient['name'] for ingredient in details.get('extendedIngredients', [])])}")
        st.write(f"**Source:** [Link to Recipe]({details['sourceUrl']})")
        st.write(f"**Instructions:** {details.get('instructions', 'No instructions available.')}")
        
        recipe_text = generate_recipe_text(recipe, details)
        st.download_button(
            label="Download Recipe",
            data=recipe_text,
            file_name=f"{details['title'].replace(' ', '_')}.txt",
            mime="text/plain"
        )

def main():
    st.title("Recipe Search")

    # Initialize session state variables
    if 'initial_query_fetched' not in st.session_state:
        st.session_state.initial_query_fetched = False
        st.session_state.recipes = []
        st.session_state.initial_query = "Indian"
    
    # Search box in the middle of the page
    st.write("<div style='text-align: center;'>", unsafe_allow_html=True)
    query = st.text_input("Search for recipes", value=st.session_state.initial_query, key="search_box")
    st.write("</div>", unsafe_allow_html=True)

    # Fetch initial recipes if not already fetched
    if not st.session_state.initial_query_fetched:
        st.session_state.recipes = fetch_recipes(st.session_state.initial_query)
        st.session_state.initial_query_fetched = True

    # Display recipes
    if query:
        st.session_state.recipes = fetch_recipes(query)
        if st.session_state.recipes:
            st.subheader(f"Top 10 Recipes for '{query}'")
            cols = st.columns(2)  
            for i, recipe in enumerate(st.session_state.recipes):
                with cols[i % len(cols)]:
                    display_recipe(recipe)
        else:
            st.write("No recipes found.")
    else:
        if st.session_state.recipes:
            st.subheader(f"Top 10 Recipes for '{st.session_state.initial_query}'")
            cols = st.columns(2)  
            for i, recipe in enumerate(st.session_state.recipes):
                with cols[i % len(cols)]:
                    display_recipe(recipe)

    # Button to try random cuisine
    cuisines = ["Indian", "Japanese", "Mexican", "Italian", "Chinese", "French", "Thai", "Spanish"]
    if st.button("Try Random Cuisine"):
        random_cuisine = random.choice(cuisines)
        st.session_state.search_box = random_cuisine
        st.session_state.recipes = fetch_recipes(random_cuisine)
        st.session_state.initial_query_fetched = True
        if st.session_state.recipes:
            st.subheader(f"Top 10 Recipes for '{random_cuisine}'")
            cols = st.columns(2)  
            for i, recipe in enumerate(st.session_state.recipes):
                with cols[i % len(cols)]:
                    display_recipe(recipe)
        else:
            st.write("No recipes found.")

if __name__ == "__main__":
    main()
