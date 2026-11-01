
import streamlit as st
import requests
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

st.title("Smoothie Ordering App")

st.write("Choose the fruits you want in your smoothie!")

smoothiefroot_data = smoothiefroot_response.json()

st.write("Available fruits in API:")
st.json(smoothiefroot_data)
session = Session.builder.configs(
    st.secrets["connections"]["snowflake"]
).create()

# Get fruit names from the FRUIT_OPTIONS table
fruit_names_df = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

fruit_names_list = [
    row["FRUIT_NAME"] for row in fruit_names_df.collect()
]

fruit_names_pd_df = fruit_names_df.to_pandas()

# Allow users to select ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_names_list,
    max_selections=5
)

# Get customer name
name_on_order = st.text_input("Name on order:")

# Display selected ingredients
if ingredients_list:
    st.write("Your selected ingredients:", ingredients_list)

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ", "

        search_on = fruit_names_pd_df.loc[
            fruit_names_pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write("API search name:", search_on)

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{requests.utils.quote(search_on)}"
        )

        smoothiefroot_data = smoothiefroot_response.json()

        st.write(f"Fruit details for {fruit_chosen}:")
        st.json(smoothiefroot_data)

    ingredients_string = ingredients_string.rstrip(", ")
    st.write("Ingredients string:", ingredients_string)

# Submit the order
if st.button("Submit Order"):
    if ingredients_list and name_on_order.strip():

        # Build the SQL insert statement
        my_insert_stmt = """
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS
            (INGREDIENTS, NAME_ON_ORDER)
            VALUES (?, ?)
        """

        session.sql(
            my_insert_stmt,
            params=[ingredients_string, name_on_order.strip()]
        ).collect()

        st.success(
            "Your smoothie is ordered for "
            + name_on_order.strip()
            + "! ✅"
        )

    else:
        st.warning("Please select ingredients and enter your name.")
