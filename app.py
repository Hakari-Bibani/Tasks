import streamlit as st
import pandas as pd
from handler import DatabaseHandler
import uuid

# Initialize database connection
db_handler = DatabaseHandler()

# Main Streamlit app
def main():
    st.title("Task Management App")

    # Board selection
    board = st.selectbox("Select a Board", ["Board 1", "Board 2", "Board 3", "Board 4", "Board 5", "Board 6"])
    board_table = f"table{board.split()[-1]}"

    # Load tasks from the selected board
    tasks = db_handler.get_tasks(board_table)

    # Create columns
    col1, col2, col3, col4 = st.columns(4)
    columns = {
        "Tasks": col1,
        "In Progress": col2,
        "Done": col3,
        "BrainStorm": col4
    }

    # Display tasks in columns
    for column, tasks_list in tasks.items():
        with columns[column]:
            st.write(f"### {column}")
            for task in tasks_list:
                st.write(f"#### {task['task']}")
                if st.button("Delete", key=f"delete_{task['id']}"):
                    if st.session_state.get(f"confirm_delete_{task['id']}"):
                        db_handler.delete_task(board_table, task['id'])
                        st.experimental_rerun()
                    else:
                        st.session_state[f"confirm_delete_{task['id']}"] = True
                        st.write("Are you sure you want to delete?")
                else:
                    st.session_state[f"confirm_delete_{task['id']}"] = False

    # Add new task
    new_task = st.text_input("Add a new task")
    if st.button("Add Task"):
        db_handler.add_task(board_table, new_task)
        st.experimental_rerun()

if __name__ == "__main__":
    main()
