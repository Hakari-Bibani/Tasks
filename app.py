import streamlit as st
import pandas as pd
from handle import DatabaseHandler
import uuid

# Initialize database handler
db = DatabaseHandler()  # No need to pass connection string anymore
# Initialize database handler
CONNECTION_STRING = "postgresql://neondb_owner:npg_vJSrcVfZ7N6a@ep-snowy-bar-a5zv1qhw-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
db = DatabaseHandler(CONNECTION_STRING)

# Initialize session state
if 'authenticated_tasks' not in st.session_state:
    st.session_state.authenticated_tasks = set()

def main():
    st.title("Task Management System")
    
    # Table selection
    table_number = st.sidebar.selectbox("Select Table", range(1, 7), format_func=lambda x: f"Table {x}")
    
    # Create new task
    with st.sidebar.expander("Create New Task"):
        create_new_task(table_number)

    # Main content area with columns for different statuses
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.header("Tasks")
        display_tasks(table_number, "Task")
        
    with col2:
        st.header("In Progress")
        display_tasks(table_number, "In Progress")
        
    with col3:
        st.header("Done")
        display_tasks(table_number, "Done")
        
    with col4:
        st.header("BrainStorm")
        display_tasks(table_number, "BrainStorm")

def create_new_task(table_number):
    content = st.text_area("Task Content")
    password = st.text_input("Set Password", type="password")
    status = st.selectbox("Initial Status", ["Task", "In Progress", "Done", "BrainStorm"])
    
    if st.button("Create Task"):
        if content and password:
            task_id = str(uuid.uuid4())
            if db.create_task(table_number, task_id, password, content, status):
                st.success("Task created successfully!")
                st.experimental_rerun()
            else:
                st.error("Failed to create task")
        else:
            st.warning("Please fill in all fields")

def display_tasks(table_number, status):
    tasks_df = db.get_tasks(table_number)
    
    if not tasks_df.empty:
        for idx, row in tasks_df.iterrows():
            task_id = row['id']
            content = row[status]
            
            if pd.notna(content):
                with st.container():
                    # Task container with border
                    st.markdown("""
                        <style>
                        .task-container {
                            border: 1px solid #ddd;
                            padding: 10px;
                            margin: 5px 0;
                            border-radius: 5px;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f'<div class="task-container">', unsafe_allow_html=True)
                    
                    # Check if task is authenticated
                    if task_id not in st.session_state.authenticated_tasks:
                        password = st.text_input(f"Password for task {task_id[:8]}", type="password", key=f"pwd_{task_id}")
                        if st.button("Unlock", key=f"unlock_{task_id}"):
                            if db.verify_password(table_number, task_id, password):
                                st.session_state.authenticated_tasks.add(task_id)
                                st.experimental_rerun()
                            else:
                                st.error("Incorrect password")
                    else:
                        # Display task content and controls
                        st.write(content)
                        
                        # Move task buttons
                        cols = st.columns(2)
                        with cols[0]:
                            new_status = st.selectbox(
                                "Move to",
                                [s for s in ["Task", "In Progress", "Done", "BrainStorm"] if s != status],
                                key=f"move_{task_id}"
                            )
                        with cols[1]:
                            if st.button("Move", key=f"btn_move_{task_id}"):
                                if db.update_task_status(table_number, task_id, content, new_status):
                                    st.success("Task moved successfully!")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to move task")
                        
                        # Delete task button
                        if st.button("Delete", key=f"delete_{task_id}"):
                            if st.button("Confirm Delete", key=f"confirm_delete_{task_id}"):
                                if db.delete_task(table_number, task_id):
                                    st.session_state.authenticated_tasks.remove(task_id)
                                    st.success("Task deleted successfully!")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to delete task")
                    
                    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
