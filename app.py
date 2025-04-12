# app.py
import streamlit as st
import streamlit_authenticator as stauth
import json
from handle import initialize_table, get_tasks, add_task, update_tasks
# For an improved drag-and-drop experience, consider integrating a component like streamlit-sortable.

# --- INITIAL SETUP AND AUTHENTICATION ---

# Initialize the table (and the default row) if needed
initialize_table()

# Load credentials from secrets
credentials = st.secrets["credentials"]

# Create the authenticator object
authenticator = stauth.Authenticate(
    credentials["usernames"],
    credentials["cookie"]["name"],
    credentials["cookie"]["key"],
    credentials["cookie"]["expiry_days"]
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.sidebar.write(f"Welcome, {name}!")
    st.title("Kanban Board")
    
    # --- COLUMN DEFINITIONS ---
    # The mapping between UI names and database column names.
    # (Note: Our DB table uses "BrainStorm" while the header is "Brainstorm".)
    columns_mapping = {
       "Task": "Task",
       "In Progress": "\"In Progress\"",
       "Done": "Done",
       "Brainstorm": "BrainStorm"
    }
    
    # Layout the columns using Streamlit's layout
    col1, col2, col3, col4 = st.columns(4)
    cols_ui = [("Task", col1), ("In Progress", col2), ("Done", col3), ("Brainstorm", col4)]
    
    # Dictionary to hold new task lists (if users edit via the text area)
    updated_tasks = {}
    
    for header, col in cols_ui:
        with col:
            st.header(header)
            # Load the tasks from the DB (stored as a JSON list in the text field)
            tasks = get_tasks(columns_mapping[header])
            # Show the tasks as JSON (this example uses a text area for simplicity)
            tasks_json = json.dumps(tasks, indent=2)
            new_tasks_json = st.text_area(f"{header} Tasks (JSON)", tasks_json, height=300, key=header)
            try:
                updated_tasks[header] = json.loads(new_tasks_json)
            except Exception:
                st.error("The JSON format is invalid. Please fix the value.")
            
            # Input and button to add a new task
            new_task = st.text_input(f"Add new task to {header}", key=f"new_{header}")
            if st.button(f"Add Task to {header}", key=f"button_{header}") and new_task:
                add_task(columns_mapping[header], new_task)
                st.experimental_rerun()  # refresh the app after adding a task

    # Save any manual changes to JSON (for example, if you implement drag-and-drop later)
    if st.button("Save Changes"):
        for header, tasks_list in updated_tasks.items():
            update_tasks(columns_mapping[header], tasks_list)
        st.success("Tasks updated successfully!")
    
    authenticator.logout("Logout", "sidebar")

elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
