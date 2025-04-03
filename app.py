import streamlit as st
import pandas as pd
from handler import DatabaseHandler
import uuid

# Set page config
st.set_page_config(
    page_title="Task Board Manager",
    page_icon="📋",
    layout="wide"
)

# Initialize session state
if "current_board" not in st.session_state:
    st.session_state.current_board = None
if "current_board_password" not in st.session_state:
    st.session_state.current_board_password = None

# Database connection
@st.cache_resource
def get_db_handler():
    return DatabaseHandler()

db = get_db_handler()

# Sidebar for board selection
with st.sidebar:
    st.title("Task Board Manager")
    
    # Board selection section
    st.header("Select Board")
    board_options = ["Board 1", "Board 2", "Board 3", "Board 4", "Board 5", "Board 6"]
    board_mapping = {
        "Board 1": "table1",
        "Board 2": "table2",
        "Board 3": "table3",
        "Board 4": "table4",
        "Board 5": "table5",
        "Board 6": "table6"
    }
    
    selected_board = st.selectbox("Choose a board", board_options)
    board_table = board_mapping[selected_board]
    
    # Password section
    password = st.text_input("Enter board password", type="password")
    
    if st.button("Access Board"):
        # Authenticate or create board if it doesn't exist
        if db.authenticate_board(board_table, password):
            st.session_state.current_board = board_table
            st.session_state.current_board_password = password
            st.success(f"Accessed {selected_board} successfully!")
            st.rerun()
        else:
            if st.sidebar.button("Create New Board"):
                db.create_board(board_table, password)
                st.session_state.current_board = board_table
                st.session_state.current_board_password = password
                st.success(f"Created {selected_board} successfully!")
                st.rerun()
            else:
                st.error("Incorrect password or board doesn't exist")

    # Logout button
    if st.session_state.current_board:
        if st.button("Logout"):
            st.session_state.current_board = None
            st.session_state.current_board_password = None
            st.rerun()

# Main content area
if st.session_state.current_board:
    st.title(f"Task Board: {next(name for name, table in board_mapping.items() if table == st.session_state.current_board)}")
    
    # Get tasks from the database
    tasks = db.get_all_tasks(st.session_state.current_board, st.session_state.current_board_password)
    
    # Convert to DataFrame for easier manipulation
    if tasks:
        df = pd.DataFrame(tasks)
    else:
        df = pd.DataFrame(columns=["id", "Task", "In Progress", "Done", "BrainStorm"])
    
    # Create four columns
    col1, col2, col3, col4 = st.columns(4)
    
    # Task column
    with col1:
        st.subheader("Tasks")
        task_text = st.text_area("New Task", height=100, key="new_task")
        if st.button("Add Task"):
            if task_text:
                task_id = str(uuid.uuid4())
                db.add_task(
                    st.session_state.current_board,
                    st.session_state.current_board_password,
                    task_id,
                    task=task_text
                )
                st.rerun()
        
        # Display tasks
        for idx, row in df.iterrows():
            if row.get("Task"):
                with st.container(border=True):
                    st.write(row["Task"])
                    cols = st.columns([3, 1, 1, 1])
                    with cols[1]:
                        if st.button("→", key=f"task_to_progress_{row['id']}"):
                            db.move_task(
                                st.session_state.current_board,
                                st.session_state.current_board_password,
                                row["id"],
                                "Task",
                                "In Progress"
                            )
                            st.rerun()
                    with cols[2]:
                        if st.button("🧠", key=f"task_to_brain_{row['id']}"):
                            db.move_task(
                                st.session_state.current_board,
                                st.session_state.current_board_password,
                                row["id"],
                                "Task",
                                "BrainStorm"
                            )
                            st.rerun()
                    with cols[3]:
                        delete_key = f"delete_task_{row['id']}"
                        if st.button("🗑️", key=delete_key):
                            st.session_state[f"confirm_{delete_key}"] = True
                        
                        if st.session_state.get(f"confirm_{delete_key}", False):
                            confirm_cols = st.columns([1, 1])
                            with confirm_cols[0]:
                                if st.button("Yes", key=f"yes_{delete_key}"):
                                    db.delete_task(
                                        st.session_state.current_board,
                                        st.session_state.current_board_password,
                                        row["id"]
                                    )
                                    st.session_state[f"confirm_{delete_key}"] = False
                                    st.rerun()
                            with confirm_cols[1]:
                                if st.button("No", key=f"no_{delete_key}"):
                                    st.session_state[f"confirm_{delete_key}"] = False
                                    st.rerun()
    
    # In Progress column
    with col2:
        st.subheader("In Progress")
        for idx, row in df.iterrows():
            if row.get("In Progress"):
                with st.container(border=True):
                    st.write(row["In Progress"])
                    cols = st.columns([1, 1, 1, 1])
                    with cols[0]:
                        if st.button("←", key=f"progress_to_task_{row['id']}"):
                            db.move_task(
                                st.session_state.current_board,
                                st.session_state.current_board_password,
                                row["id"],
                                "In Progress",
                                "Task"
                            )
                            st.rerun()
                    with cols[1]:
                        if st.button("→", key=f"progress_to_done_{row['id']}"):
                            db.move_task(
                                st.session_state.current_board,
                                st.session_state.current_board_password,
                                row["id"],
                                "In Progress",
                                "Done"
                            )
                            st.rerun()
                    with cols[2]:
                        if st.button("🧠", key=f"progress_to_brain_{row['id']}"):
                            db.move_task(
                                st.session_state.current_board,
                                st.session_state.current_board_password,
                                row["id"],
                                "In Progress",
                                "BrainStorm"
                            )
                            st.rerun()
                    with cols[3]:
                        delete_key = f"delete_progress_{row['id']}"
                        if st.button("🗑️", key=delete_key):
                            st.session_state[f"confirm_{delete_key}"] = True
                        
                        if st.session_state.get(f"confirm_{delete_key}", False):
                            confirm_cols = st.columns([1, 1])
                            with confirm_cols[0]:
                                if st.button("Yes", key=f"yes_{delete_key}"):
                                    db.delete_task(
                                        st.session_state.current_board,
                                        st.session_state.current_board_password,
                                        row["id"]
                                    )
                                    st.session_state[f"confirm_{delete_key}"] = False
                                    st.rerun()
                            with confirm_cols[1]:
                                if st.button("No", key=f"no_{delete_key}"):
                                    st.session_state[f"confirm_{delete_key}"] = False
                                    st.rerun()
    
    # Done column
    with col3:
        st.subheader("Done")
        for idx, row in df.iterrows():
            if row.get("Done"):
                with st.container(border=True):
                    st.write(row["Done"])
                    cols = st.columns([1, 1, 1])
                    with cols[0]:
                        if st.button("←", key=f"done_to_progress_{row['id']}"):
                            db.move_task(
                                st.session_state.current_board,
                                st.session_state.current_board_password,
                                row["id"],
                                "Done",
                                "In Progress"
                            )
                            st.rerun()
                    with cols[1]:
                        if st.button("🧠", key=f"done_to_brain_{row['id']}"):
                            db.move_task(
                                st.session_state.current_board,
                                st.session_state.current_board_password,
                                row["id"],
                                "Done",
                                "BrainStorm"
                            )
                            st.rerun()
                    with cols[2]:
                        delete_key = f"delete_done_{row['id']}"
                        if st.button("🗑️", key=delete_key):
                            st.session_state[f"confirm_{delete_key}"] = True
                        
                        if st.session_state.get(f"confirm_{delete_key}", False):
                            confirm_cols = st.columns([1, 1])
                            with confirm_cols[0]:
                                if st.button("Yes", key=f"yes_{delete_key}"):
                                    db.delete_task(
                                        st.session_state.current_board,
                                        st.session_state.current_board_password,
                                        row["id"]
                                    )
                                    st.session_state[f"confirm_{delete_key}"] = False
                                    st.rerun()
                            with confirm_cols[1]:
                                if st.button("No", key=f"no_{delete_key}"):
                                    st.session_state[f"confirm_{delete_key}"] = False
                                    st.rerun()
    
    # BrainStorm column
    with col4:
        st.subheader("BrainStorm")
        brainstorm_text = st.text_area("New Brainstorm", height=100, key="new_brainstorm")
        if st.button("Add Brainstorm"):
            if brainstorm_text:
                brainstorm_id = str(uuid.uuid4())
                db.add_task(
                    st.session_state.current_board,
                    st.session_state.current_board_password,
                    brainstorm_id,
                    brainstorm=brainstorm_text
                )
                st.rerun()
        
        # Display brainstorms
        for idx, row in df.iterrows():
            if row.get("BrainStorm"):
                with st.container(border=True):
                    st.write(row["BrainStorm"])
                    cols = st.columns([1, 1, 1])
                    with cols[0]:
                        if st.button("→", key=f"brain_to_task_{row['id']}"):
                            db.move_task(
                                st.session_state.current_board,
                                st.session_state.current_board_password,
                                row["id"],
                                "BrainStorm",
                                "Task"
                            )
                            st.rerun()
                    with cols[1]:
                        if st.button("⚡", key=f"brain_to_progress_{row['id']}"):
                            db.move_task(
                                st.session_state.current_board,
                                st.session_state.current_board_password,
                                row["id"],
                                "BrainStorm",
                                "In Progress"
                            )
                            st.rerun()
                    with cols[2]:
                        delete_key = f"delete_brain_{row['id']}"
                        if st.button("🗑️", key=delete_key):
                            st.session_state[f"confirm_{delete_key}"] = True
                        
                        if st.session_state.get(f"confirm_{delete_key}", False):
                            confirm_cols = st.columns([1, 1])
                            with confirm_cols[0]:
                                if st.button("Yes", key=f"yes_{delete_key}"):
                                    db.delete_task(
                                        st.session_state.current_board,
                                        st.session_state.current_board_password,
                                        row["id"]
                                    )
                                    st.session_state[f"confirm_{delete_key}"] = False
                                    st.rerun()
                            with confirm_cols[1]:
                                if st.button("No", key=f"no_{delete_key}"):
                                    st.session_state[f"confirm_{delete_key}"] = False
                                    st.rerun()
else:
    st.info("Please select a board and enter the password to continue")
    st.write("Each board can be password protected. If a board doesn't exist, you'll have the option to create it.")
