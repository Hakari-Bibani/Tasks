import streamlit as st
import handler as db
from streamlit_draggable_list import draggable_list

# Simplified session management
st.set_page_config(layout="wide")

def main():
    st.title("Kanban Board Task Management")
    
    # Initialize session state
    if 'boards' not in st.session_state:
        st.session_state.boards = db.get_all_boards()
    if 'current_board' not in st.session_state:
        st.session_state.current_board = None
    
    # Board selection sidebar
    with st.sidebar:
        st.header("Board Management")
        new_board_name = st.text_input("Create New Board")
        if st.button("Create Board"):
            if new_board_name:
                db.create_board(new_board_name)
                st.session_state.boards = db.get_all_boards()
                st.rerun()
        
        st.divider()
        st.subheader("Select Board")
        for board in st.session_state.boards:
            if st.button(board, key=f"board_{board}"):
                st.session_state.current_board = board
    
    # Main board interface
    if st.session_state.current_board:
        display_board(st.session_state.current_board)
    else:
        st.info("Please select or create a board from the sidebar")

def display_board(board_name):
    st.header(f"Board: {board_name}")
    
    # Get current board data
    board_data = db.get_board_data(board_name)
    
    # Create columns
    cols = st.columns(4)
    column_names = ["Task", "In Progress", "Done", "BrainStorm"]
    
    # Display tasks in each column
    for i, col in enumerate(cols):
        with col:
            st.subheader(column_names[i])
            column_tasks = board_data[column_names[i]].dropna().tolist()
            
            # Display draggable list
            if column_tasks:
                new_order = draggable_list(column_tasks)
                if new_order != column_tasks:
                    # Update the database if order changed
                    db.update_column_order(board_name, column_names[i], new_order)
            
            # Add new task
            with st.expander("Add Task"):
                new_task = st.text_input("New task", key=f"new_{column_names[i]}")
                if st.button("Add", key=f"add_{column_names[i]}"):
                    if new_task:
                        db.add_task_to_board(
                            board_name,
                            db.generate_id(),
                            new_task,
                            column_names[i]
                        )
                        st.rerun()

if __name__ == "__main__":
    main()
