# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customise your smoothie :cup_with_straw:")
st.write(
  """ Choose Fruits you want in your custom smoothie""")

name_on_the_order = st.text_input("Name on the Smoothie:")
st.write("The name on the Smoothie will be:", name_on_the_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredient_list = st.multiselect('Choose up to 5 ingredients:',my_dataframe)

if ingredient_list:
    
    ingredient_string = ''

    for fruit_choosen in ingredient_list:
        ingredient_string += fruit_choosen + ' '

    time_to_insert = st.button('Submit Order')

    my_insert_stmt = """INSERT INTO smoothies.public.orders(ingredients, name_on_the_order)
                        VALUES (?, ?)"""

    if time_to_insert:
        session.sql(my_insert_stmt, params=[ingredient_string.strip(), name_on_the_order]).collect()
        st.success('Your Smoothie is ordered, ' + name_on_the_order + '!', icon="✅")
