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
    # ✅ Clean ingredients string (no extra spaces)
    ingredients_string = " ".join([fruit.strip() for fruit in ingredients_list]).strip()

    # ✅ Debug print to check spacing (remove later when all works)
    st.text(f"DEBUG Ingredients String: >{ingredients_string}<")
    st.text(f"DEBUG Name: >{name_on_order.strip()}<")

    # Convert dataframe to pandas once
    pd_df = my_dataframe.to_pandas()

    for fruit_chosen in ingredients_list:
        st.subheader(fruit_chosen + ' Nutrition Information')

        # Use SEARCH_ON for API
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)

        st.write(f"The search value for {fruit_chosen} is {search_on}")
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    # ✅ Clean name_on_order too
    clean_name = name_on_order.strip()

    # Insert statement
    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}','{clean_name}')
    """

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + clean_name + '!', icon="✅")
