import streamlit as st
import handler as db
from streamlit_sortables import sort_items
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
    
    # Prepare columns for drag-and-drop
    columns = {
        "Task": {"items": [], "title": "Tasks"},
        "In Progress": {"items": [], "title": "In Progress"},
        "Done": {"items": [], "title": "Done"},
        "BrainStorm": {"items": [], "title": "BrainStorm"}
    }
    
    # Populate columns with existing items
    for _, row in board_data.iterrows():
        for col in columns:
            if row[col]:
                columns[col]["items"].append({
                    "id": row['id'],
                    "content": row[col]
                })
    
    # Create sortable columns
    sortable_items = [
        {"header": columns[col]["title"], "items": columns[col]["items"]} 
        for col in columns
    ]
    
    # Display the sortable board
    changed = sort_items(sortable_items, multi_containers=True, direction="horizontal")
    
    # Handle changes (drag and drop)
    if changed:
        db.clear_board(st.session_state.current_board)
        for column in changed:
            col_name = column["header"]
            if col_name == "Tasks": col_name = "Task"
            for item in column["items"]:
                db.add_task_to_board(
                    st.session_state.current_board,
                    item["id"],
                    item["content"],
                    col_name
                )
    
    # Add new task
    with st.expander("Add New Task"):
        new_task_col = st.selectbox("Column", ["Task", "In Progress", "Done", "BrainStorm"])
        new_task_content = st.text_area("Task Content")
        if st.button("Add Task"):
            if new_task_content:
                db.add_task_to_board(
                    st.session_state.current_board,
                    str(uuid.uuid4()),
                    new_task_content,
                    new_task_col
                )
                st.rerun()
else:
    st.info("Please select or create a board from the sidebar")
