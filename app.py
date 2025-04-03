import streamlit as st
from handle import get_board_data, save_board_data

def mark_unsaved(column_list_name, task_state_key, index):
    """Callback to mark state as unsaved and update the task list with edited text."""
    # Update the specific task text in the list based on the current value of the text input
    st.session_state[column_list_name][index] = st.session_state[task_state_key]
    st.session_state["unsaved_changes"] = True

# Page configuration
st.set_page_config(page_title="Task Management Board", layout="wide")

# Title of the app
st.title("Task Management App")
st.caption("Manage tasks across multiple boards with columns for different stages.")

# Note: Drag-and-drop functionality is not implemented in this app.
# Placeholder: This is where one could integrate a drag-and-drop feature for moving tasks between columns.

# Board selection
board_options = {f"Board {i}": f"table{i}" for i in range(1, 7)}
selected_board = st.selectbox("Select a Board", list(board_options.keys()))
table_name = board_options[selected_board]

# Load data from the selected board (table)
try:
    tasks, in_progress, done, brainstorm = get_board_data(table_name)
except Exception as e:
    st.error(f"Failed to load data for {selected_board}: {e}")
    st.stop()

# If the user switches boards, we may lose unsaved changes.
# Inform the user (in a real app, we might prompt to save or auto-save on board switch).
if "current_board" in st.session_state and st.session_state.current_board != table_name:
    # Reset session state for tasks from previous board
    for key in list(st.session_state.keys()):
        if key.startswith(st.session_state.current_board):
            del st.session_state[key]
    st.session_state["unsaved_changes"] = False
# Update current board selection in session state
st.session_state.current_board = table_name

# Initialize session state lists if not already (or after board switch)
if "data" not in st.session_state or st.session_state.get("unsaved_changes", False) is False:
    st.session_state["tasks_list"] = tasks
    st.session_state["in_progress_list"] = in_progress
    st.session_state["done_list"] = done
    st.session_state["brainstorm_list"] = brainstorm
    st.session_state["unsaved_changes"] = False

# Create four columns for the four task stages
cols = st.columns(4)
column_names = [("tasks_list", "Task"), ("in_progress_list", "In Progress"), ("done_list", "Done"), ("brainstorm_list", "BrainStorm")]

# UI for each column
for (list_name, col_label), col in zip(column_names, cols):
    with col:
        st.subheader(col_label)
        # Display tasks in this column
        to_delete_index = None
        for idx, task_text in enumerate(st.session_state[list_name]):
            # Create a row with a text input and a delete button
            task_key = f"{table_name}_{list_name}_{idx}"
            # Use columns for text input and delete button on the same row
            text_col, del_col = st.columns([0.85, 0.15])
            # Text input for the task (value will persist in session_state via the key)
            text_col.text_input(label="", value=task_text, key=task_key,
                                 on_change=mark_unsaved, args=(list_name, task_key, idx))
            # Delete button (with trash emoji)
            if del_col.button("🗑️", key=f"del_{table_name}_{list_name}_{idx}"):
                to_delete_index = idx
        # If a delete button was clicked, remove that task and rerun to update UI
        if to_delete_index is not None:
            # Remove session state keys for this task and any following tasks to avoid key collisions after reindex
            old_len = len(st.session_state[list_name])
            # Pop the task from the list
            st.session_state[list_name].pop(to_delete_index)
            # Delete any leftover widget state keys for shifted indices
            for j in range(to_delete_index, old_len):
                key_j = f"{table_name}_{list_name}_{j}"
                if key_j in st.session_state:
                    del st.session_state[key_j]
            # Mark unsaved and rerun
            st.session_state["unsaved_changes"] = True
            st.experimental_rerun()
        # Input to add a new task in this column
        new_task_key = f"new_{table_name}_{list_name}"
        new_task_text = st.text_input("Add new", value="", key=new_task_key, placeholder="New task...")
        if st.button("Add", key=f"add_{table_name}_{list_name}"):
            if new_task_text:
                st.session_state[list_name].append(new_task_text)
                # Mark that there are unsaved changes
                st.session_state["unsaved_changes"] = True
                # Clear the input field by resetting its session state value
                st.session_state[new_task_key] = ""
                st.experimental_rerun()

# Save changes button
if st.button("Save Changes"):
    try:
        # Save the current lists to the database
        save_board_data(table_name,
                        st.session_state["tasks_list"],
                        st.session_state["in_progress_list"],
                        st.session_state["done_list"],
                        st.session_state["brainstorm_list"])
        st.session_state["unsaved_changes"] = False
        st.success(f"Changes saved to {selected_board}.")
    except Exception as e:
        st.error(f"Error saving changes: {e}")
