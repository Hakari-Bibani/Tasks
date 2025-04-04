import streamlit as st
from handlers import create_new_board, get_tasks

def show_sidebar():
    with st.sidebar:
        st.title("Kanban Boards")
        
        # Board selection
        current_board = st.selectbox(
            "Select Board",
            [f"table{i}" for i in range(1, 7)],
            index=0,
            key="board_selector"
        )
        st.session_state.current_board = current_board
        
        # Create new board
        new_board = st.text_input("Create New Board")
        if st.button("Create Board") and new_board:
            create_new_board(new_board)
            st.success(f"Board {new_board} created!")
            st.experimental_rerun()
        
        # Statistics
        st.subheader("Statistics")
        for column in ["Task", "In Progress", "Done", "BrainStorm"]:
            tasks = get_tasks(current_board, column)
            st.metric(column, len(tasks))
