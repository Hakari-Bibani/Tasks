import streamlit as st
import json
from handler import get_board, create_board, add_card, delete_card, move_card

st.title("Kanban Board Task Management")

# Sidebar: Choose a board/table
board_options = ["table1", "table2", "table3", "table4", "table5", "table6"]
selected_table = st.sidebar.selectbox("Select Board", board_options)

# Sidebar: Password input
password_input = st.sidebar.text_input("Enter Board Password", type="password")

# Use the table name as the board id (for simplicity)
board_id = selected_table

# Attempt to load the board from the database
board_data = get_board(selected_table, board_id)

# If the board doesn't exist, allow creation with a provided password.
if board_data is None:
    if password_input:
        create_board(selected_table, board_id, password_input)
        st.success("Board created!")
        board_data = get_board(selected_table, board_id)
    else:
        st.warning("This board does not exist. Enter a password to create it.")
        st.stop()

# Check that the entered password matches the board’s password.
if board_data["password"] and password_input != board_data["password"]:
    st.error("Incorrect password!")
    st.stop()

st.success("Authenticated!")

st.markdown("## Kanban Board")
columns = ["Task", "In Progress", "Done", "BrainStorm"]

# Display each Kanban column using Streamlit columns
col_layout = st.columns(4)
for idx, col_name in enumerate(columns):
    with col_layout[idx]:
        st.header(col_name)
        cards = board_data[col_name]
        # List each card with options to delete or move it.
        for i, card in enumerate(cards):
            st.write(card)
            # Delete button for each card
            if st.button(f"Delete card {i+1}", key=f"delete_{col_name}_{i}"):
                delete_card(selected_table, board_id, col_name, i)
                st.experimental_rerun()
            # Provide a select box for moving the card to another column.
            target_cols = [c for c in columns if c != col_name]
            target = st.selectbox("Move to", target_cols, key=f"move_{col_name}_{i}")
            if st.button(f"Move card {i+1}", key=f"move_btn_{col_name}_{i}"):
                move_card(selected_table, board_id, col_name, target, i)
                st.experimental_rerun()
        
        # Input for adding a new card to the current column.
        new_card = st.text_input(f"New card in {col_name}", key=f"new_card_{col_name}")
        if st.button(f"Add card to {col_name}", key=f"add_{col_name}") and new_card:
            add_card(selected_table, board_id, col_name, new_card)
            st.experimental_rerun()
