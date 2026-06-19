# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write("Choose the fruits you want in your custom Smoothie!")

# Name Input
name_on_the_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_the_order)

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get Fruit Data
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert Snowpark DataFrame to Pandas
pd_df = my_dataframe.to_pandas()

# Fruit Selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        # Lookup SEARCH_ON value
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        st.write(
            'The search value for',
            fruit_chosen,
            'is',
            search_on,
            '.'
        )

        st.subheader(
            fruit_chosen + ' Nutrition Information'
        )

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Submit Order Button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:

        try:

            safe_ingredients = ingredients_string.strip().replace("'", "''")
            safe_name = name_on_the_order.replace("'", "''")

            my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders
            (ingredients, name_on_order)
            VALUES
            ('{safe_ingredients}', '{safe_name}')
            """

            st.code(my_insert_stmt)

            session.sql(my_insert_stmt).collect()

            st.success(
                'Your Smoothie is ordered, ' + name_on_the_order + '!',
                icon="✅"
            )

        except Exception as e:
            st.error("INSERT failed!")
            st.exception(e)
