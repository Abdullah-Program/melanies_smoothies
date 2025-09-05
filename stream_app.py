# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: name on smoothie
name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Query fruit options (convert to list for Streamlit)
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
fruit_list = [row['FRUIT_NAME'] for row in my_dataframe]

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

if ingredients_list:
    # Build string of chosen ingredients
    ingredients_string = ' '.join(ingredients_list)

    # SQL Insert Statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string}')
    """

    st.write(my_insert_stmt)

    # Submit button
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie for {name_on_order} is ordered! ✅")
