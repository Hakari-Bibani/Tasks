import streamlit as st
from handler import (
    create_board,
    get_board_data,
    add_card,
    delete_card,
    move_card,
    list_boards,
)

# Page Configuration
st.set_page_config(page_title="Task Management App", layout="wide")

# Initialize session state for board selection
if "current_board" not in st.session_state:
    st.session_state.current_board = None

# Sidebar: Board Selection
st.sidebar.title("Boards")
boards = list_boards()
board_name = st.sidebar.selectbox("Select a Board", ["Create New Board"] + boards)

if board_name == "Create New Board":
    new_board_name = st.sidebar.text_input("Enter New Board Name")
    if st.sidebar.button("Create"):
        if new_board_name.strip():
            create_board(new_board_name)
            st.sidebar.success(f"Board '{new_board_name}' created!")
            st.experimental_rerun()
        else:
            st.sidebar.error("Board name cannot be empty.")
else:
    st.session_state.current_board = board_name

# Main Content
if st.session_state.current_board:
    st.title(f"Board: {st.session_state.current_board}")

    # Fetch data for the current board
    board_data = get_board_data(st.session_state.current_board)

    # Define columns for the board interface
    col_tasks, col_in_progress, col_done, col_brainstorm = st.columns(4)

    # Helper function to render cards in a column
    def render_column(column_key, column_name):
        with column_key:
            st.subheader(column_name)
            for card_id, content in board_data.get(column_name, {}).items():
                with st.expander(content):
                    st.markdown(f"**ID:** {card_id}")
                    if st.button(f"Delete {card_id}", key=f"delete_{card_id}"):
                        if st.session_state.get(f"confirm_delete_{card_id}", False):
                            delete_card(st.session_state.current_board, card_id)
                            st.success("Card deleted!")
                            st.experimental_rerun()
                        else:
                            st.warning("Are you sure?")
                            if st.button("Yes", key=f"confirm_{card_id}"):
                                st.session_state[f"confirm_delete_{card_id}"] = True
                                st.experimental_rerun()

    # Render columns
    render_column(col_tasks, "Tasks")
    render_column(col_in_progress, "In Progress")
    render_column(col_done, "Done")
    render_column(col_brainstorm, "BrainStorm")

    # Add new card form
    with st.form("add_card_form"):
        st.subheader("Add a New Card")
        column = st.selectbox("Select Column", ["Tasks", "In Progress", "Done", "BrainStorm"])
        content = st.text_area("Card Content")
        submitted = st.form_submit_button("Add Card")
        if submitted:
            if content.strip():
                add_card(st.session_state.current_board, column, content)
                st.success("Card added!")
                st.experimental_rerun()
            else:
                st.error("Card content cannot be empty.")
