# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write("Choose the fruits you want in your custom Smoothie!")

# Customer name
name_on_the_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_the_order)

# Filled checkbox
order_filled = st.checkbox("Mark order as filled")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit data
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert to pandas
pd_df = my_dataframe.to_pandas()

# Fruit selector
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        # Get SEARCH_ON value
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        st.subheader(
            fruit_chosen + ' Nutrition Information'
        )

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Submit button
    if st.button("Submit Order"):

        try:

            safe_ingredients = ingredients_string.strip().replace("'", "''")
            safe_name = name_on_the_order.replace("'", "''")

            my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders
            (
                NAME_ON_ORDER,
                INGREDIENTS,
                ORDER_FILLED
            )
            VALUES
            (
                '{safe_name}',
                '{safe_ingredients}',
                {str(order_filled).upper()}
            )
            """

            session.sql(my_insert_stmt).collect()

            st.success(
                f"Your Smoothie is ordered, {name_on_the_order}!",
                icon="✅"
            )

        except Exception as e:
            st.error("Insert failed")
            st.exception(e)
