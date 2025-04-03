import streamlit as st
import handler

# Initialize session state for delete confirmation
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = None

def main():
    st.title("Task Management Board")

    # Sidebar: choose board (database table)
    board = st.sidebar.selectbox("Select Board", 
                                 ["table1", "table2", "table3", "table4", "table5", "table6"])

    # Load tasks from the chosen table
    tasks = handler.get_tasks(board)
    
    # Define the four board columns
    col_names = ["Task", "In Progress", "Done", "BrainStorm"]
    cols = st.columns(len(col_names))
    
    # Organize tasks by status
    tasks_by_status = {col: [] for col in col_names}
    for task in tasks:
        status = task.get("status")
        if status in tasks_by_status:
            tasks_by_status[status].append(task)
    
    # Display each column with its tasks/cards
    for idx, col_name in enumerate(col_names):
        with cols[idx]:
            st.header(col_name)
            for task in tasks_by_status[col_name]:
                st.info(task["content"])
                # Delete functionality with confirmation
                if st.button("🗑 Delete", key=f"del_{task['id']}"):
                    st.session_state.confirm_delete = task["id"]
                if st.session_state.confirm_delete == task["id"]:
                    st.warning("Are you sure you want to delete?")
                    if st.button("Confirm Delete", key=f"confirm_{task['id']}"):
                        handler.delete_task(board, task["id"])
                        st.session_state.confirm_delete = None
                        st.experimental_rerun()
                # “Move” functionality: select a new column (simulate drag-and-drop)
                new_status = st.selectbox(
                    "Move to",
                    [name for name in col_names if name != col_name],
                    key=f"move_{task['id']}"
                )
                if st.button("Move", key=f"move_btn_{task['id']}"):
                    handler.update_task_position(board, task["id"], new_status)
                    st.experimental_rerun()

    st.markdown("---")
    st.subheader("Add New Task")
    with st.form("new_task_form"):
        task_content = st.text_area("Task Content")
        task_password = st.text_input("Password", type="password")
        initial_status = st.selectbox("Place task in", col_names)
        submitted = st.form_submit_button("Add Task")
        if submitted and task_content.strip() != "":
            handler.add_task(board, task_content, task_password, initial_status)
            st.experimental_rerun()

if __name__ == "__main__":
    main()
