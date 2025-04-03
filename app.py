import streamlit as st
from streamlit_sortables import sort_items
import handler

# Initialize database (create tables if not exist)
handler.init_db()

st.title("Kanban Board")

# Fetch available boards
boards = handler.get_boards()

# If no boards, prompt to create the first board
if not boards:
    st.subheader("No boards available. Create a new board:")
    new_board_name = st.text_input("Board name", key="new_board_name")
    if st.button("Create Board"):
        if new_board_name.strip():
            new_id = handler.add_board(new_board_name.strip())
            if new_id:
                st.success(f"Board '{new_board_name}' created!")
                # Select the new board and refresh
                st.session_state.selected_board = new_board_name.strip()
                st.experimental_rerun()
            else:
                st.warning(f"Board '{new_board_name}' already exists. Please use a different name.")
        else:
            st.warning("Please enter a valid board name.")
    st.stop()  # Stop here until a board is created

# Board selection
board_names = [b["name"] for b in boards]
# Ensure a valid selected_board in session_state
if "selected_board" not in st.session_state or st.session_state.selected_board not in board_names:
    st.session_state.selected_board = board_names[0]
selected_board = st.selectbox("Select Board", board_names, index=board_names.index(st.session_state.selected_board), key="selected_board")

# Section to add a new board (when at least one board exists already)
st.write("### Add a New Board")
new_board = st.text_input("New board name", value="", key="new_board_input")
if st.button("Create Board", key="create_board_btn"):
    if new_board.strip():
        new_id = handler.add_board(new_board.strip())
        if new_id:
            st.success(f"Board '{new_board}' created!")
            # Auto-select the newly created board
            st.session_state.selected_board = new_board.strip()
            st.experimental_rerun()
        else:
            st.warning(f"Board '{new_board}' already exists.")
    else:
        st.warning("Board name cannot be empty.")

# Refresh boards list (in case a new board was added)
boards = handler.get_boards()
current_board = next((b for b in boards if b["name"] == st.session_state.selected_board), None)
current_board_id = current_board["id"] if current_board else None

# Section to add a new card
st.write("### Add a New Card")
new_card_text = st.text_input("Card title", value="", key="new_card_text")
new_card_col = st.selectbox("Add to column", ["Tasks", "In Progress", "Done", "BrainStorm"], index=0, key="new_card_col")
if st.button("Add Card", key="add_card_btn"):
    if new_card_text.strip():
        handler.add_card(current_board_id, new_card_col, new_card_text.strip())
        st.success(f"Added card to **{new_card_col}**.")
        # Clear the input and refresh to show the new card
        st.session_state.new_card_text = ""
        st.experimental_rerun()
    else:
        st.warning("Card title cannot be empty.")

# Fetch all cards for the current board from the database
tasks = handler.get_tasks(current_board_id)

# Section to delete a card
st.write("### Delete a Card")
if tasks:
    # List cards as "[ID] title" for unique identification
    options = [f"[{t['id']}] {t['content']}" for t in tasks]
    delete_choice = st.selectbox("Select card to delete", options, key="delete_choice")
    if st.button("Delete Card", key="delete_card_btn"):
        if delete_choice:
            # Parse the selected "[ID] title" to get the ID
            task_id = int(delete_choice.split("]")[0].strip("["))
            handler.delete_card(task_id)
            st.success("Card deleted.")
            st.experimental_rerun()
else:
    st.write("_No cards to delete._")

# Prepare data for the draggable board columns
COLUMNS = ["Tasks", "In Progress", "Done", "BrainStorm"]
# Group tasks by column name
col_items = {col: [] for col in COLUMNS}
for t in tasks:
    col_items[t["column"]].append(t)
# Sort tasks within each column by their position
for col in COLUMNS:
    col_items[col].sort(key=lambda x: x["position"])
# Build the data structure for streamlit-sortables
original_items = [
    {"header": col, "items": [f"[{t['id']}] {t['content']}" for t in col_items[col]]}
    for col in COLUMNS
]

# Render the sortable multi-column board (draggable cards)
sorted_items = sort_items(original_items, multi_containers=True, key=f"board-{current_board_id}")

# If the user dragged/dropped cards, update positions in the database
if sorted_items != original_items:
    # Create a lookup of original positions for each task id
    orig_positions = {t["id"]: (t["column"], t["position"]) for t in tasks}
    # Loop through each container (column) in the new order
    for container in sorted_items:
        col_name = container["header"]
        for pos, item in enumerate(container["items"]):
            # Each item is "[ID] title"
            item_id = int(item.split("]")[0].strip("["))
            orig_col, orig_pos = orig_positions.get(item_id, (None, None))
            # If column or position changed, update the task in DB
            if orig_col != col_name or orig_pos != pos:
                handler.move_card(item_id, col_name, pos)
    # After updating all changes, refresh the app to reflect new order
    st.experimental_rerun()
