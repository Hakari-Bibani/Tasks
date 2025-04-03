import streamlit as st
import handler as db
from streamlit_draggable_list import draggable_list
import uuid

# Initialize database
db.init_db()

# Page configuration
st.set_page_config(layout="wide")
st.title("Kanban Board Task Management")

# Initialize session state
if 'boards' not in st.session_state:
    st.session_state.boards = db.get_all_boards()
if 'current_board' not in st.session_state:
    st.session_state.current_board = None

# Sidebar for board management
with st.sidebar:
    st.header("Board Management")
    
    # Create new board
    new_board_name = st.text_input("New Board Name")
    if st.button("Create Board"):
        if new_board_name:
            db.create_board(new_board_name)
            st.session_state.boards = db.get_all_boards()
            st.session_state.current_board = new_board_name
            st.rerun()
    
    st.divider()
    st.subheader("Your Boards")
    
    # Board selection
    for board in st.session_state.boards:
        if st.button(board, key=f"board_{board}"):
            st.session_state.current_board = board

# Main board display
if st.session_state.current_board:
    st.header(f"Board: {st.session_state.current_board}")
    
    # Get board data
    board_data = db.get_board_data(st.session_state.current_board)
    
    # Create columns
    cols = st.columns(4)
    column_names = ["Task", "In Progress", "Done", "BrainStorm"]
    
    for i, col in enumerate(cols):
        with col:
            st.subheader(column_names[i])
            
            # Get tasks for this column
            tasks = []
            if not board_data.empty:
                tasks = board_data[column_names[i]].dropna().tolist()
            
            # Display draggable list
            if tasks:
                new_order = draggable_list(tasks)
                if new_order != tasks:
                    db.update_column_tasks(st.session_state.current_board, column_names[i], new_order)
            
            # Add new task
            with st.expander("➕ Add Task"):
                new_task = st.text_input("Task content", key=f"new_{column_names[i]}")
                if st.button("Add", key=f"add_{column_names[i]}"):
                    if new_task:
                        db.add_task(
                            board_name=st.session_state.current_board,
                            task_id=str(uuid.uuid4()),
                            content=new_task,
                            column=column_names[i]
                        )
                        st.rerun()
else:
    st.info("Please select or create a board from the sidebar")
