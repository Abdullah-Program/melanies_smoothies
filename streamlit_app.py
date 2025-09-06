# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd
import re

# Write directly to the app
st.title("🥤Customize Your Smoothie!🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# User input for name
name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)
pd_df = my_dataframe.to_pandas()

# Ingredient selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    # Build clean ingredients string
    ingredients_string = " ".join(ingredients_list)
    ingredients_string = re.sub(r"\s+", " ", ingredients_string)  # collapse multiple spaces
    ingredients_string = ingredients_string.strip()               # trim ends
    ingredients_string = ingredients_string.replace("\u00A0", " ")  # replace NBSP

    # Loop over fruits and fetch nutrition
    for fruit_chosen in ingredients_list:
        # Lookup the search_on value (safe fallback = fruit name)
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
        ].iloc[0] if not pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
        ].empty else fruit_chosen

        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )
        if smoothiefroot_response.status_code == 200:
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.warning(f"No data found for {fruit_chosen}")

    # Insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string}')
    """

    st.write("SQL Preview:", my_insert_stmt)
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie for {name_on_order} is ordered!", icon="✅")
