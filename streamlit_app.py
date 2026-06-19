# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Page Title
st.title(":cup_with_straw: Customize your Smoothie :cup_with_straw:")
st.write("Choose fruits you want in your custom smoothie")

# Customer Name
name_on_the_order = st.text_input("Name on the Smoothie:")
st.write("The name on the Smoothie will be:", name_on_the_order)

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get Fruit Options from Snowflake
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

# Convert Snowflake DataFrame to Python List
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Fruit Selection
ingredient_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Order Submission
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

# Smoothie Fruit API Example
st.subheader("Fruit Nutrition Information")

smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)

if smoothiefroot_response.status_code == 200:
    fruit_data = smoothiefroot_response.json()

    # Convert JSON response to DataFrame
    fruit_df = pd.DataFrame([fruit_data])

    st.dataframe(
        fruit_df,
        use_container_width=True
    )
else:
    st.error("Unable to fetch fruit information.")
