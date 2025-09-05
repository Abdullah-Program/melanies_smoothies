# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f"🥤Customize Your Smoothie!🥤")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    ,my_dataframe
    ,max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # Correct INSERT statement for your table structure
    # Only specify name_on_order and ingredients - the other fields have defaults
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders (name_on_order, ingredients)
        VALUES ('""" + name_on_order + """', '""" + ingredients_string + """')
    """

    st.write(my_insert_stmt)
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
      
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie for {name_on_order} is ordered!", icon="✅")
      
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
