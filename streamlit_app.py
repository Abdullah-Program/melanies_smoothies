# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Title
st.title("🥤Customize Your Smoothie!🥤")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

# Input: name on order
name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options with SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get correct search term from SEARCH_ON column
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Show Nutrition Info section
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        try:
            sf_df = pd.DataFrame.from_dict(smoothiefroot_response.json(), orient='index', columns=['value'])
            st.dataframe(sf_df, use_container_width=True)
        except:
            st.warning(f"No nutrition data found for {fruit_chosen}")

    # Insert order into Snowflake
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string.strip()}')
    """

    st.write(my_insert_stmt)  # Debugging - can remove later
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie for {name_on_order} is ordered!", icon="✅")
