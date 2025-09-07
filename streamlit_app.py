# Import Python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customize Your Smoothie :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)

# User input for name on order
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be: ", name_on_order)

try:
    # Establish connection to Snowflake
    cnx = st.connection("snowflake")
    session = cnx.session()

    # Retrieve fruit options from Snowflake
    my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

    # Convert to pandas DataFrame and plain Python list
    pd_df = my_dataframe.to_pandas()
    fruit_options = pd_df["FRUIT_NAME"].tolist()

    # Multi-select for choosing ingredients
    ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_options, max_selections=5)

    # Process ingredients selection
    if ingredients_list:
        # Clean join of ingredients (remove extra spaces, ensure single space)
        ingredients_string = " ".join(fruit.strip() for fruit in ingredients_list)

        # Debug print for checking invisible spaces
        st.text(f"DEBUG INGREDIENTS: [{ingredients_string}] (len={len(ingredients_string)})")

        # Loop through chosen fruits to fetch details
        for fruit_chosen in ingredients_list:
            try:
                fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
                fruityvice_response.raise_for_status()

                if fruityvice_response.status_code == 200:
                    st.dataframe(data=fruityvice_response.json(), use_container_width=True)
                else:
                    st.warning(f"Failed to fetch details for {fruit_chosen}")

            except requests.exceptions.RequestException as e:
                st.error(f"Failed to fetch details for {fruit_chosen}: {str(e)}")

        # SQL statement (correct column order: name_on_order, ingredients)
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (name_on_order, ingredients)
            VALUES ('{name_on_order}', '{ingredients_string}')
        """

        # Button to submit order
        time_to_insert = st.button('Submit Order')
        if time_to_insert:
            try:
                session.sql(my_insert_stmt).collect()
                st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
            except Exception as e:
                st.error(f"Failed to submit order: {str(e)}")

except Exception as ex:
    st.error(f"An error occurred: {str(ex)}")
