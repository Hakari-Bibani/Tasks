"""
sidebar.py

Displays the Streamlit sidebar for selecting existing tables or creating new ones.
"""

import streamlit as st
from handle import get_connection

def show_sidebar():
    """
    Creates a sidebar with:
    - A selectbox for existing tables (hard-coded or dynamically fetched)
    - A text_input and button to create new tables
    Returns the currently selected table name (str).
    """
    st.sidebar.header("Select a Table / Board")

    # Hardcode or fetch these from the DB. Let's just hardcode for simplicity:
    existing_tables = ["table1", "table2", "table3", "table4", "table5", "table6"]
    chosen_table = st.sidebar.selectbox("Pick a Board (Table)", existing_tables)

    st.sidebar.write("---")
    new_table_name = st.sidebar.text_input("Create a new table (board)")

    if st.sidebar.button("Create Table"):
        if new_table_name:
            create_table_if_not_exists(new_table_name)
            st.success(f"Table '{new_table_name}' has been created.")
            st.experimental_rerun()

    return chosen_table

def create_table_if_not_exists(table_name: str):
    """
    Creates a new table with the standard columns if it doesn't already exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id TEXT PRIMARY KEY,
            "Task" TEXT,
            "In Progress" TEXT,
            "Done" TEXT,
            "BrainStorm" TEXT
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
