import streamlit as st
import streamlit_kanban  # Custom component for Kanban boards
import handler          # Our database handler module

# Initialize the database (create tables if not exists)
handler.init_db()

# Load existing board names from the database
board_names = handler.get_board_names()

st.title("Kanban Task Management App")

# Section to create a new board (if fewer than 6 boards exist)
if len(board_names) < 6:
    with st.expander("Create a new board"):
        new_board_name = st.text_input("Board name", key="new_board_name")
        if st.button("Create Board", key="create_board_btn"):
            if new_board_name.strip() == "":
                st.error("Please enter a name for the board.")
            else:
                new_id = handler.create_board(new_board_name.strip())
                if new_id:
                    st.success(f"Board '{new_board_name}' created! Select it from the dropdown.")
                    board_names = handler.get_board_names()  # refresh the board list
                else:
                    st.error("Maximum of 6 boards reached. Cannot create another board.")

# If no boards exist yet, prompt to create one
if not board_names:
    st.write("No boards available. Create a board to get started.")
else:
    # Board selection dropdown
    board_options = [f"{bid}: {name}" for bid, name in board_names.items()]
    selected_option = st.selectbox("Select Board", board_options, key="selected_board")
    # Parse the selection (format "id: name")
    current_board_id = int(selected_option.split(":")[0])
    current_board_name = board_names[current_board_id]

    st.subheader(f"Board: {current_board_name}")

    # Prepare the Kanban data structure for the selected board
    state_key = f'board_data_{current_board_id}'
    if state_key not in st.session_state:
        # Fetch tasks from the database for this board
        tasks = handler.fetch_tasks(current_board_id)
        # Define the Kanban columns data as expected by streamlit-kanban component&#8203;:contentReference[oaicite:6]{index=6}
        col_mapping = {
            "Task": {"id": "task", "title": "Tasks"},
            "In Progress": {"id": "in-progress", "title": "In Progress"},
            "Done": {"id": "done", "title": "Done"},
            "BrainStorm": {"id": "brainstorm", "title": "BrainStorm"}
        }
        # Optional color mapping for card labels
        color_map = {
            "task": "#F7D794",        # light orange
            "in-progress": "#82CCDD", # light blue
            "done": "#78E08F",        # light green
            "brainstorm": "#E77F67"   # light red
        }
        columns_data = []
        for col_name, col_info in col_mapping.items():
            cards = []
            for item in tasks[col_name]:
                content = item["content"]
                # Append trash icon to the task name for display
                display_text = content + " 🗑️"
                cards.append({
                    "id": item["id"],
                    "name": display_text,
                    "fields": [],  # e.g., tags/labels; left empty here
                    "color": color_map.get(col_info["id"], "#FFFFFF")
                })
            columns_data.append({
                "id": col_info["id"],
                "title": col_info["title"],
                "cards": cards
            })
        st.session_state[state_key] = {"columns": columns_data}
    # Retrieve the current board data from session state
    board_data = st.session_state[state_key]

    # Render the Kanban board component for the current board
    kanban_output = streamlit_kanban.kanban(board_data, key=f"kanban_board_{current_board_id}")

    # Handle drag-and-drop updates (if the Kanban component returned data after a move)
    if kanban_output is not None:
        new_data = kanban_output
        # Determine which task(s) changed column by comparing old vs new positions
        def get_positions(data):
            return {card["id"]: col["id"] 
                    for col in data["columns"] for card in col["cards"]}
        old_positions = get_positions(board_data)
        new_positions = get_positions(new_data)
        for task_id, new_col in new_positions.items():
            old_col = old_positions.get(task_id)
            if new_col != old_col:
                # Find the card's text from new_data and remove the trash icon
                content = None
                for col in new_data["columns"]:
                    for card in col["cards"]:
                        if card["id"] == task_id:
                            content = card["name"].replace(" 🗑️", "")
                            break
                    if content is not None:
                        break
                # Update the task's status in the database
                if content is not None:
                    handler.update_task_status(current_board_id, task_id, new_col, content)
        # Save the updated board state to session
        st.session_state[state_key] = new_data
        board_data = new_data

    # Section to add a new task to any column
    st.markdown("**Add New Task:**")
    add_cols = st.columns(4)
    col_info_list = [
        ("Tasks", "Task", "task"),
        ("In Progress", "In Progress", "in-progress"),
        ("Done", "Done", "done"),
        ("BrainStorm", "BrainStorm", "brainstorm")
    ]
    for (col_title, col_db, col_id), col in zip(col_info_list, add_cols):
        with col:
            new_task_text = st.text_input(col_title, key=f"new_task_{col_id}_{current_board_id}")
            if st.button("Add", key=f"add_btn_{col_id}_{current_board_id}"):
                if new_task_text.strip() == "":
                    st.warning("Task description cannot be empty.")
                else:
                    # Insert the new task into the database (in the specified column)
                    new_task_id = handler.add_task(current_board_id, col_db, new_task_text.strip())
                    if new_task_id:
                        # Append the new card to the board data in session state
                        new_card = {
                            "id": new_task_id,
                            "name": new_task_text.strip() + " 🗑️",
                            "fields": [],
                            "color": "#FFFFFF"
                        }
                        for col_data in board_data["columns"]:
                            if col_data["id"] == col_id:
                                col_data["cards"].append(new_card)
                                break
                        st.session_state[state_key] = board_data
                        # Rerun to refresh the UI (clear input, etc.)
                        st.experimental_rerun()

    # Section to manage (delete) tasks, with confirmation dialog
    with st.expander("Manage / Delete Tasks", expanded=st.session_state.get("confirm_delete", False)):
        for col in board_data["columns"]:
            st.write(f"**{col['title']}**")
            for card in col["cards"]:
                task_text = card["name"].replace(" 🗑️", "")
                delete_key = f"delete_{current_board_id}_{card['id']}"
                if st.button("Delete", key=delete_key):
                    # Store deletion target in session state and prompt for confirmation
                    st.session_state.delete_target = {"board": current_board_id,
                                                      "id": card["id"], "content": task_text}
                    st.session_state.confirm_delete = True
                    st.experimental_rerun()
        # If a delete action was triggered, show confirmation prompt&#8203;:contentReference[oaicite:7]{index=7}
        if st.session_state.get("confirm_delete"):
            target = st.session_state.get("delete_target", {})
            if target:
                st.error(f"Are you sure you want to delete **{target['content']}**?")
                confirm_col, cancel_col = st.columns(2)
                with confirm_col:
                    if st.button("Yes, delete"):
                        # Delete the task from the database
                        handler.delete_task(target["board"], target["id"])
                        # Remove the task card from the session state data
                        data = st.session_state[f'board_data_{target["board"]}']
                        for col in data["columns"]:
                            col["cards"] = [c for c in col["cards"] if c["id"] != target["id"]]
                        st.session_state[f'board_data_{target["board"]}'] = data
                        st.success(f"Task '{target['content']}' has been deleted.")
                        # Reset deletion state and refresh
                        st.session_state.confirm_delete = False
                        st.session_state.delete_target = None
                        st.experimental_rerun()
                with cancel_col:
                    if st.button("Cancel"):
                        st.session_state.confirm_delete = False
                        st.session_state.delete_target = None
                        st.experimental_rerun()
