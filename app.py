import streamlit as st
from sidebar import render_sidebar, get_current_board
from handlers import get_tasks_for_board, update_task_status, add_task, edit_task, delete_task
from utils import render_kanban_board

def main():
    st.set_page_config(page_title="Modern Kanban Board", layout="wide")
    
    # Sidebar: board management
    board = render_sidebar()
    st.write(f"Current Board: {board['board_name']}")
    
    # Get tasks for the current board
    tasks = get_tasks_for_board(board_id=board['board_id'])
    
    # Render the Kanban board with drag-and-drop functionality
    updated_tasks = render_kanban_board(tasks)

    # Process drag-and-drop updates (this could be implemented with session_state callbacks)
    if st.session_state.get("status_changed"):
        task_id = st.session_state["changed_task_id"]
        new_status = st.session_state["new_status"]
        update_task_status(task_id, new_status)
        st.experimental_rerun()  # refresh to get updated tasks

if __name__ == "__main__":
    main()
