import streamlit as st
import handler
from datetime import datetime
import uuid

def initialize_session_state():
    if 'current_board' not in st.session_state:
        st.session_state.current_board = None

def create_card(column, table_name):
    with st.container():
        card_content = st.text_area(f"Add new card to {column}", key=f"new_{column}_{uuid.uuid4()}")
        if st.button("Add", key=f"add_{column}_{uuid.uuid4()}"):
            if card_content:
                handler.add_card(table_name, column, card_content)
                st.experimental_rerun()

def show_card(card_id, content, column, table_name):
    col1, col2 = st.columns([5, 1])
    with col1:
        st.text_area("", value=content, key=f"card_{card_id}", height=100)
    with col2:
        if st.button("🗑️", key=f"delete_{card_id}"):
            if st.button("Confirm Delete", key=f"confirm_delete_{card_id}"):
                handler.delete_card(table_name, card_id)
                st.experimental_rerun()

def main():
    st.title("Task Management Board")
    initialize_session_state()

    # Board selection
    tables = ['table1', 'table2', 'table3', 'table4', 'table5', 'table6']
    selected_board = st.selectbox("Select Board", tables)
    st.session_state.current_board = selected_board

    if st.session_state.current_board:
        columns = ['Task', 'In Progress', 'Done', 'BrainStorm']
        cols = st.columns(len(columns))

        # Display columns
        for idx, column in enumerate(columns):
            with cols[idx]:
                st.subheader(column)
                create_card(column, st.session_state.current_board)
                
                # Display existing cards
                cards = handler.get_cards(st.session_state.current_board, column)
                for card in cards:
                    show_card(card['id'], card[column], column, st.session_state.current_board)

if __name__ == "__main__":
    main()
