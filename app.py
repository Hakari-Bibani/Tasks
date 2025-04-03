import streamlit as st
from streamlit_sortables import sort_items  # Drag-and-drop component
import handler

st.set_page_config(page_title="Kanban Board", layout="wide")

# --- Authentication ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Login form for board selection and password
if not st.session_state["authenticated"]:
    st.title("Kanban Board Login")
    board_choice = st.selectbox("Select Board", ["Board 1", "Board 2", "Board 3", "Board 4", "Board 5", "Board 6"])
    board_table = f"table{board_choice.split()[-1]}"  # maps "Board 1" -> "table1", etc.
    password_input = st.text_input("Board Password", type="password")
    if st.button("Open Board"):
        if handler.verify_password(board_table, password_input):
            st.session_state["authenticated"] = True
            st.session_state["board_table"] = board_table
            st.session_state["board_password"] = password_input
            st.experimental_rerun()
        else:
            st.error("Invalid password. Please try again.")

# Main Kanban board interface (only if authenticated)
if st.session_state["authenticated"]:
    board_table = st.session_state["board_table"]
    st.title(f"Kanban Board – {board_table}")

    # Fetch current board data (tasks in each column)
    board_data = handler.get_board_data(board_table)
    # board_data is a dict with keys "Task", "In Progress", "Done", "BrainStorm"
    # Each value is a list of (id, text) tuples for cards in that column.
    # Prepare data for drag-and-drop component (list of dicts per column)&#8203;:contentReference[oaicite:0]{index=0}
    original_items = []
    id_to_text = {}      # map card id to text
    id_to_column = {}    # map card id to its current column
    for col_name, cards in board_data.items():
        texts = []
        for card_id, text in cards:
            texts.append(text)
            id_to_text[card_id] = text
            id_to_column[card_id] = col_name
        original_items.append({"header": col_name, "items": texts})

    # Display the Kanban columns with draggable cards
    sorted_items = sort_items(original_items, multi_containers=True)
    # If any card was moved between columns, update the database accordingly
    if sorted_items and sorted_items != original_items:
        for container in sorted_items:
            new_col = container["header"]
            for text in container["items"]:
                # Find the card's id via its text
                card_id = None
                for cid, txt in id_to_text.items():
                    if txt == text:
                        card_id = cid
                        break
                if card_id is None:
                    continue
                old_col = id_to_column.get(card_id)
                if old_col and old_col != new_col:
                    handler.update_card_column(board_table, card_id, old_col, new_col)
        st.experimental_rerun()  # reload data to reflect changes

    # Handle card deletion with confirmation
    if "confirm_delete" in st.session_state:
        # Confirmation prompt in a modal dialog
        with st.dialog("Confirm Deletion"):
            card_id = st.session_state.confirm_delete
            st.write(f"Are you sure you want to delete this task: **{id_to_text.get(card_id, '')}**?")
            col1, col2 = st.columns(2)
            if col1.button("Yes, delete"):
                handler.delete_card(board_table, card_id)
                st.success("Card deleted.")
                st.session_state.pop("confirm_delete", None)
                st.experimental_rerun()
            if col2.button("Cancel"):
                st.session_state.pop("confirm_delete", None)
                st.experimental_rerun()

    # Add a trash icon button for each card (displayed on the card)
    for col_name, cards in board_data.items():
        for card_id, text in cards:
            btn_label = f"🗑️ Delete {text}"
            if st.button(btn_label, key=f"del_{card_id}"):
                st.session_state.confirm_delete = card_id
                st.experimental_rerun()

    # New task input
    st.markdown("---")
    st.subheader("Add New Task")
    new_text = st.text_input("Task description", key="new_task_text")
    new_col = st.selectbox("Add to column:", ["Task", "In Progress", "Done", "BrainStorm"], key="new_task_col")
    if st.button("Add Task"):
        if new_text.strip():
            handler.add_card(board_table, st.session_state["board_password"], new_col, new_text.strip())
            st.success(f"Added task to **{new_col}** column.")
            st.experimental_rerun()
        else:
            st.error("Please enter some text for the task.")
