# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")

st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Customer Name
name_on_the_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_the_order)

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fruit Options Table
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(col("FRUIT_NAME"))

# Convert Snowpark DataFrame to list
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Fruit Selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Nutrition Information + Order
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        st.subheader(fruit_chosen + ' Nutrition Information')

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    time_to_insert = st.button('Submit Order')

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
