import streamlit as st
import handle
import uuid

st.set_page_config(page_title="MaisterTask Clone", layout="wide")

# Initialize session state variables
if 'board' not in st.session_state:
    st.session_state.board = None
if 'table' not in st.session_state:
    st.session_state.table = None
if 'board_id' not in st.session_state:
    st.session_state.board_id = None
if 'password' not in st.session_state:
    st.session_state.password = None

st.sidebar.title("Board Access")
mode = st.sidebar.selectbox("Select Mode", ["Load Board", "Create Board"])

with st.sidebar.form(key="board_form"):
    table_choice = st.selectbox("Select Table", 
                                ["table1", "table2", "table3", "table4", "table5", "table6"])
    board_id_input = st.text_input("Board ID")
    password_input = st.text_input("Password", type="password")
    submit_button = st.form_submit_button(label="Submit")

if submit_button:
    st.session_state.table = table_choice
    st.session_state.board_id = board_id_input
    st.session_state.password = password_input
    if mode == "Create Board":
        # Create a new board with empty columns
        handle.create_board(table_choice, board_id_input, password_input)
        st.success("Board created. You can now add tasks.")
    # Load board from DB
    board = handle.get_board(table_choice, board_id_input, password_input)
    if board:
        st.session_state.board = board
    else:
        st.error("Board not found or incorrect password.")

if st.session_state.board:
    st.title(f"Board: {st.session_state.board_id} ({st.session_state.table})")
    
    # Define the four columns
    col_names = ["Task", "In Progress", "Done", "BrainStorm"]
    columns = st.columns(4)

    # For each column, display header, tasks, and a form to add a new task.
    for idx, col in enumerate(columns):
        col_name = col_names[idx]
        with col:
            st.header(col_name)
            tasks = st.session_state.board[col_name]
            for task in tasks:
                with st.container():
                    st.write(task)
                    # Simulated “drag-and-drop”: select a target column to move the task
                    target = st.selectbox(
                        f"Move '{task}' to", 
                        options=[n for n in col_names if n != col_name],
                        key=f"move_{task}"
                    )
                    if st.button("Move", key=f"move_btn_{task}"):
                        handle.move_task_in_board(st.session_state.table, 
                                                    st.session_state.board, 
                                                    col_name, target, task)
                        st.success(f"Task moved to {target}.")
                        st.experimental_rerun()
                    # Delete button with confirmation
                    if st.button("Delete", key=f"delete_{task}"):
                        confirm = st.checkbox("Are you sure?", key=f"confirm_{task}")
                        if confirm:
                            handle.delete_task_from_board(st.session_state.table, 
                                                            st.session_state.board, 
                                                            col_name, task)
                            st.success("Task deleted.")
                            st.experimental_rerun()
            # Form to add a new task in this column
            new_task = st.text_input(f"Add new task to {col_name}", key=f"new_{col_name}")
            if st.button(f"Add Task to {col_name}", key=f"add_{col_name}") and new_task:
                handle.add_task_to_board(st.session_state.table, 
                                         st.session_state.board, 
                                         col_name, new_task)
                st.success("Task added.")
                st.experimental_rerun()
