# Import python packages
import requests
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie.
    """)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'), col('SEARCH_ON'))

name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)
ingredients_list = st.multiselect('Choose up to 5 ingredients:', my_dataframe, max_selections=5)

if ingredients_list:
    # Build ingredients string cleanly with join (no trailing spaces)
    ingredients_string = ' '.join(ingredients_list)

    pd_df = my_dataframe.to_pandas()  # Move outside loop for efficiency

    for fruit_chosen in ingredients_list:
        st.subheader(fruit_chosen + ' Nutrition Information')

        # Use SEARCH_ON only for API
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)

        st.write(f"The search value for {fruit_chosen} is {search_on}")
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    # ✅ Build insert statement inside the same block
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
