import streamlit as st
from handle import get_tables, add_table

def display_sidebar():
    st.sidebar.header("Boards")
    # Get a list of existing tables/boards
    tables = get_tables()
    selected_table = st.sidebar.selectbox("Select Board", tables)
    
    st.sidebar.subheader("Create New Board")
    new_table_name = st.sidebar.text_input("New Board Name")
    if st.sidebar.button("Create Board"):
        if new_table_name:
            add_table(new_table_name)
            st.experimental_rerun()
    return selected_table
