# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Name Input
name_on_the_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_the_order)

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get Fruit Data from Snowflake
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert to Pandas
fruit_df = my_dataframe.to_pandas()

# Dictionary: GUI Name -> API Search Name
fruit_dict = dict(
    zip(
        fruit_df["FRUIT_NAME"],
        fruit_df["SEARCH_ON"]
    )
)

# Fruit names for the multiselect
fruit_list = fruit_df["FRUIT_NAME"].tolist()

# Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Nutrition Information
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        st.subheader(
            fruit_chosen + " Nutrition Information"
        )

        search_value = fruit_dict[fruit_chosen]

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_value
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Submit Order Button
    time_to_insert = st.button("Submit Order")

    if time_to_insert:

        safe_ingredients = ingredients_string.strip().replace("'", "''")
        safe_name = name_on_the_order.replace("'", "''")

        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order)
        VALUES
        ('{safe_ingredients}', '{safe_name}')
        """

        session.sql(my_insert_stmt).collect()

        st.success(
            'Your Smoothie is ordered, ' + name_on_the_order + '!',
            icon="✅"
        )
