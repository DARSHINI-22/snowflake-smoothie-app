
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

st.title("Smoothie Ordering App")

st.write("Choose the fruits you want in your smoothie!")

session = get_active_session()

# Get fruit names from the FRUIT_OPTIONS table
fruit_names_df = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).select(col("FRUIT_NAME"))

fruit_names_list = [
    row["FRUIT_NAME"] for row in fruit_names_df.collect()
]

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

    # Convert the list into a string
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ", "

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
