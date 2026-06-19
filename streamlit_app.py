# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App Title
st.title(":cup_with_straw: Customize your Smoothie :cup_with_straw:")
st.write("Choose Fruits you want in your custom smoothie")

# Customer Name
name_on_the_order = st.text_input("Name on the Smoothie:")
st.write("The name on the Smoothie will be:", name_on_the_order)

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit list from Snowflake
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Fruit Selection
ingredient_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Show Nutrition Information
if ingredient_list:

    st.subheader("Fruit Nutrition Information")

    for fruit_chosen in ingredient_list:

        try:
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}"
            )

            if smoothiefroot_response.status_code == 200:

                fruit_data = smoothiefroot_response.json()

                st.write(f"### {fruit_chosen}")

                fruit_df = pd.DataFrame([fruit_data])

                st.dataframe(
                    fruit_df,
                    use_container_width=True
                )

            else:
                st.warning(
                    f"Could not retrieve nutrition data for {fruit_chosen}"
                )

        except Exception as e:
            st.error(f"Error retrieving data for {fruit_chosen}: {e}")

# Submit Order
if ingredient_list:

    ingredient_string = " ".join(ingredient_list)

    time_to_insert = st.button("Submit Order")

    if time_to_insert:

        safe_ingredients = ingredient_string.replace("'", "''")
        safe_name = name_on_the_order.replace("'", "''")

        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order)
        VALUES
        ('{safe_ingredients}', '{safe_name}')
        """

        session.sql(my_insert_stmt).collect()

        st.success(
            f"Your Smoothie is ordered, {name_on_the_order}!",
            icon="✅"
        )
