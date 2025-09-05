# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch FRUIT_NAME + SEARCH_ON from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Multiselect only shows FRUIT_NAME
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    chosen_data = []  # store mappings for UI

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Look up correct search value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        chosen_data.append({"FRUIT_NAME": fruit_chosen, "SEARCH_ON": search_on})

        # Show mapping sentence (optional)
        st.info(f"The search value for {fruit_chosen} is {search_on}.")

        # Fetch nutrition info
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        try:
            sf_df = pd.DataFrame.from_dict(smoothiefroot_response.json(), orient='index', columns=['value'])
            st.dataframe(sf_df, use_container_width=True)
        except:
            st.warning(f"No nutrition data found for {fruit_chosen}")

    # Show FRUIT_NAME → SEARCH_ON mapping table
    st.dataframe(pd.DataFrame(chosen_data), use_container_width=True)

    # Insert into orders
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string}')
    """
    st.write(my_insert_stmt)

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie for {name_on_order} is ordered!", icon="✅")
