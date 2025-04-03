import streamlit as st
from streamlit_sortables import sort_items
from handler import get_board_data, add_card, move_card, delete_card

# Page configuration for better layout
st.set_page_config(page_title="Task Management", layout="wide")

# Sidebar for selecting one of the six boards
board = st.sidebar.selectbox("Select Board", [f"table{i}" for i in range(1,7)])

# Title and subtitle
st.title("Task Management Board")
st.subheader(f"Board: {board}")

# Load the tasks for the selected board from the database
tasks, in_progress, done, brainstorm = get_board_data(board)

# Prepare data structure for the drag-and-drop component (multi-column lists)
board_structure = [
    {"header": "Tasks", "items": [content for (_, content) in tasks]},
    {"header": "In Progress", "items": [content for (_, content) in in_progress]},
    {"header": "Done",    "items": [content for (_, content) in done]},
    {"header": "BrainStorm", "items": [content for (_, content) in brainstorm]}
]

# Display the draggable Kanban board and capture any changes (drag-and-drop)
sorted_structure = sort_items(board_structure, multi_containers=True)

# Check if any card was moved to a different column and update the database
if sorted_structure != board_structure:
    # Create a lookup from content to (id, original_column) for all cards
    content_map = {}
    for (id_val, content) in tasks:
        content_map[content] = (id_val, "Tasks")
    for (id_val, content) in in_progress:
        content_map[content] = (id_val, "In Progress")
    for (id_val, content) in done:
        content_map[content] = (id_val, "Done")
    for (id_val, content) in brainstorm:
        content_map[content] = (id_val, "BrainStorm")
    # Iterate through new sorted structure to detect column changes
    for container in sorted_structure:
        new_col = container["header"]
        for content in container["items"]:
            if content in content_map:
                card_id, old_col = content_map[content]
                if new_col != old_col:
                    # Update the database to move the card to the new column
                    move_card(board, card_id, old_col, new_col, content)
    # Refresh data after moving cards
    tasks, in_progress, done, brainstorm = get_board_data(board)

# Layout four columns for Tasks, In Progress, Done, BrainStorm
col1, col2, col3, col4 = st.columns(4)

# Helper to render a column of cards with delete and add functionality
def render_column(column_container, cards, col_name):
    with column_container:
        st.markdown(f"**{col_name}**")  # Column header
        for (id_val, content) in cards:
            # Each card displayed with a delete button (icon) next to it
            card_col, del_col = st.columns([4, 1])
            card_col.write(content)
            if del_col.button("❌", key=f"delete-{id_val}"):
                # If delete icon clicked, mark this card for deletion (confirmation next)
                st.session_state["to_delete"] = (id_val, content)
        # Input field and button to add a new card in this column
        new_task = st.text_input(f"Add to {col_name}", "", key=f"newtask-{board}-{col_name}")
        if st.button(f"Add {col_name}", key=f"add-{board}-{col_name}"):
            if new_task:
                add_card(board, col_name, new_task)
                # Clear input and refresh the app to show the new card
                st.session_state[f"newtask-{board}-{col_name}"] = ""
                st.experimental_rerun()

# Render each of the four columns with cards
render_column(col1, tasks, "Tasks")
render_column(col2, in_progress, "In Progress")
render_column(col3, done, "Done")
render_column(col4, brainstorm, "BrainStorm")

# If a delete action was initiated, show a confirmation prompt
if "to_delete" in st.session_state:
    delete_id, delete_content = st.session_state["to_delete"]
    st.warning(f"Are you sure you want to delete the card: '{delete_content}'?")
    confirm_col, cancel_col = st.columns([1, 1])
    if confirm_col.button("Yes, delete"):
        delete_card(board, delete_id)
        # Remove the flag and refresh
        del st.session_state["to_delete"]
        st.experimental_rerun()
    if cancel_col.button("Cancel"):
        # Cancel deletion
        del st.session_state["to_delete"]
        st.experimental_rerun()
