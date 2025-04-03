import streamlit as st
from streamlit_dragndrop import dragndrop
from handler import DatabaseHandler

# Initialize database handler
db_handler = DatabaseHandler()

# Sidebar for board management
st.sidebar.header("Task Boards")
boards = db_handler.get_all_boards()
selected_board = st.sidebar.selectbox("Select Board", boards)

if st.sidebar.button("Create New Board"):
    new_board_name = st.sidebar.text_input("Enter Board Name")
    if st.sidebar.button("Create") and new_board_name:
        db_handler.create_board(new_board_name)
        st.experimental_rerun()

# Main application
st.title(f"Task Board: {selected_board}")

# Create columns
columns = st.columns(4)
column_names = ["Tasks", "In Progress", "Done", "BrainStorm"]

# Create drag and drop interface
with dragndrop(columns, ["Tasks", "In Progress", "Done", "BrainStorm"]) as dnd:
    for col_idx, col_name in enumerate(column_names):
        cards = db_handler.get_cards(selected_board, col_name)
        with columns[col_idx]:
            st.header(col_name)
            for card_id, content in cards.items():
                with st.expander(content, expanded=False):
                    st.write(content)
                    if st.button("🗑️", key=f"delete_{card_id}"):
                        if st.confirmation("Are you sure you want to delete this card?"):
                            db_handler.delete_card(selected_board, card_id)
                            st.experimental_rerun()
            
            # Add new card
            new_card_content = st.text_area(f"Add new card to {col_name}", key=f"new_{col_name}")
            if st.button(f"Add to {col_name}", key=f"add_{col_name}"):
                if new_card_content:
                    db_handler.add_card(selected_board, col_name, new_card_content)
                    st.experimental_rerun()

# Handle drag and drop
if dnd:
    card_id = dnd["card_id"]
    from_col = dnd["from"]
    to_col = dnd["to"]
    db_handler.move_card(selected_board, card_id, to_col)
    st.experimental_rerun()
