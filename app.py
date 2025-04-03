import streamlit as st
import uuid
import handler

# Set page configuration
st.set_page_config(page_title="Task Management App", layout="wide")

# List of available boards (each corresponds to one table)
boards = ["table1", "table2", "table3", "table4", "table5", "table6"]

# Sidebar: select a board
board_selected = st.sidebar.selectbox("Select Board", boards)
st.title(f"Board: {board_selected}")

# Initialize session state for delete confirmation (one pending deletion at a time)
if "pending_delete" not in st.session_state:
    st.session_state.pending_delete = None

# Load tasks for the selected board.
# The tasks function returns a dict with keys for each column (i.e. "Task", "In Progress", "Done", "BrainStorm")
tasks = handler.get_tasks(board_selected)

# Define the column names (these must match the table column names exactly)
column_names = ["Task", "In Progress", "Done", "BrainStorm"]

# Create four columns in the Streamlit layout
cols = st.columns(4)

# For each board column, display its header, list its cards, and add a form to add new cards.
for col, col_name in zip(cols, column_names):
    with col:
        st.header(col_name)

        # Display each card in the current column
        for card in tasks.get(col_name, []):
            card_id, content = card

            st.info(content)  # Display the card content in an info box

            # Provide a "Move" option using a select box (simulate drag-and-drop)
            new_status = st.selectbox(
                "Move to",
                options=[status for status in column_names if status != col_name],
                key=f"move_{card_id}"
            )
            if st.button("Move", key=f"move_btn_{card_id}"):
                handler.update_task(board_selected, card_id, new_status)
                st.experimental_rerun()  # Refresh the page to show updates

            # Delete functionality with a two-step confirmation.
            if st.button("Delete", key=f"delete_{card_id}"):
                st.session_state.pending_delete = card_id

            # If this card is pending deletion, show confirmation options.
            if st.session_state.pending_delete == card_id:
                st.warning("Are you sure you want to delete?")
                if st.button("Confirm Delete", key=f"confirm_delete_{card_id}"):
                    handler.delete_task(board_selected, card_id)
                    st.session_state.pending_delete = None
                    st.experimental_rerun()
                if st.button("Cancel", key=f"cancel_delete_{card_id}"):
                    st.session_state.pending_delete = None

        # Form to add a new card to the current column.
        with st.form(key=f"add_form_{col_name}"):
            new_content = st.text_input("New Card", key=f"new_{col_name}")
            submit = st.form_submit_button("Add Card")
            if submit and new_content:
                # Generate a new unique ID for the card
                new_id = str(uuid.uuid4())
                handler.add_task(board_selected, col_name, new_id, new_content)
                st.experimental_rerun()
