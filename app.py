import streamlit as st
from handler import DatabaseHandler
import time
from datetime import datetime
import uuid

# Initialize database handler
db = DatabaseHandler()

def init_session_state():
    if 'current_board' not in st.session_state:
        st.session_state.current_board = None

def create_card(column, table_name):
    card_id = str(uuid.uuid4())
    content = st.text_area(f"New card in {column}", key=f"new_{column}_{time.time()}")
    if st.button(f"Add to {column}", key=f"add_{column}_{time.time()}"):
        if content.strip():
            # Create a dictionary with all columns set to None except the target column
            data = {
                'id': card_id,
                'Task': content if column == 'Task' else None,
                'In Progress': content if column == 'In Progress' else None,
                'Done': content if column == 'Done' else None,
                'BrainStorm': content if column == 'BrainStorm' else None
            }
            db.insert_card(table_name, data)
            st.experimental_rerun()

def display_card(card, column, table_name):
    with st.container():
        col1, col2 = st.columns([5, 1])
        with col1:
            st.text_area("", value=card[column], key=f"card_{card['id']}_{column}", 
                        on_change=lambda: db.update_card(table_name, card['id'], column, 
                        st.session_state[f"card_{card['id']}_{column}"]))
        with col2:
            if st.button("🗑️", key=f"delete_{card['id']}"):
                if st.button("Confirm Delete", key=f"confirm_delete_{card['id']}"):
                    db.delete_card(table_name, card['id'])
                    st.experimental_rerun()

def main():
    st.title("Task Management Board")
    init_session_state()

    # Board selection
    tables = ["table1", "table2", "table3", "table4", "table5", "table6"]
    selected_board = st.selectbox("Select Board", tables)
    st.session_state.current_board = selected_board

    if st.session_state.current_board:
        # Create columns for the board
        cols = st.columns(4)
        columns = ['Task', 'In Progress', 'Done', 'BrainStorm']
        
        # Display each column
        for i, column in enumerate(columns):
            with cols[i]:
                st.subheader(column)
                create_card(column, st.session_state.current_board)
                
                # Display existing cards
                cards = db.get_cards(st.session_state.current_board)
                for card in cards:
                    if card[column]:
                        display_card(card, column, st.session_state.current_board)

        # Add some CSS to make it look better
        st.markdown("""
        <style>
        .stTextArea textarea {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
        }
        .stButton button {
            width: 100%;
            margin: 2px 0;
        }
        </style>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
