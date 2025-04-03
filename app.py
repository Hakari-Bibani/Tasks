import streamlit as st
import handler
import json

# Configure page
st.set_page_config(page_title="Kanban Board", layout="wide")

# Initialize database connection (read from st.secrets)
if "db_initialized" not in st.session_state:
    conn_str = st.secrets["postgres"]["connection_string"]
    handler.init_db(conn_str)
    st.session_state.db_initialized = True

# Sidebar: choose mode and target table
mode = st.sidebar.radio("Select Mode", ["Create Board", "Access Board"])
table_options = ["table1", "table2", "table3", "table4", "table5", "table6"]
selected_table = st.sidebar.selectbox("Select Table", table_options)

if mode == "Create Board":
    st.header("Create New Board")
    board_id = st.text_input("Board ID (Unique)")
    password = st.text_input("Password", type="password")
    if st.button("Create Board"):
        existing = handler.get_board(selected_table, board_id)
        if existing:
            st.error("A board with that ID already exists!")
        elif board_id.strip() == "" or password.strip() == "":
            st.error("Please provide a board ID and password.")
        else:
            handler.create_board(selected_table, board_id, password)
            st.success("Board created successfully!")
            st.info("Now switch to 'Access Board' mode in the sidebar to manage your board.")

elif mode == "Access Board":
    st.header("Access Board")
    board_id = st.text_input("Board ID", key="access_board_id")
    password = st.text_input("Password", type="password", key="access_password")
    if st.button("Access Board"):
        board = handler.get_board(selected_table, board_id)
        if board is None:
            st.error("Board not found!")
        elif board["password"] != password:
            st.error("Incorrect password!")
        else:
            st.success("Board accessed!")
            st.session_state.board = board
            st.session_state.table = selected_table
            st.session_state.board_id = board_id

# Main Kanban interface – only shown if a board has been successfully accessed
if "board" in st.session_state:
    # Load board data into session state (convert JSON strings back to lists)
    if "board_data" not in st.session_state:
        st.session_state.board_data = {
            "Tasks": st.session_state.board["Task"],
            "In Progress": st.session_state.board["In Progress"],
            "Done": st.session_state.board["Done"],
            "BrainStorm": st.session_state.board["BrainStorm"]
        }

    st.subheader(f"Kanban Board: {st.session_state.board_id} (Table: {st.session_state.table})")
    columns_list = ["Tasks", "In Progress", "Done", "BrainStorm"]
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]

    # Display each column
    for idx, col_name in enumerate(columns_list):
        with cols[idx]:
            st.markdown(f"### {col_name}")
            cards = st.session_state.board_data[col_name]
            # List existing cards
            for i, card in enumerate(cards):
                st.markdown(f"**Card {i+1}:**")
                st.write(card)

                # Delete card with confirmation
                if st.button("Delete", key=f"delete_{col_name}_{i}"):
                    confirm = st.checkbox("Are you sure?", key=f"confirm_{col_name}_{i}")
                    if confirm:
                        st.session_state.board_data[col_name].pop(i)
                        handler.update_board(
                            st.session_state.table,
                            st.session_state.board_id,
                            {
                                "Task": st.session_state.board_data["Tasks"],
                                "In Progress": st.session_state.board_data["In Progress"],
                                "Done": st.session_state.board_data["Done"],
                                "BrainStorm": st.session_state.board_data["BrainStorm"],
                            },
                        )
                        st.experimental_rerun()

                # Move card: choose target column (cannot be the current one)
                move_options = [option for option in columns_list if option != col_name]
                target_column = st.selectbox("Move to", move_options, key=f"move_select_{col_name}_{i}")
                if st.button("Move", key=f"move_button_{col_name}_{i}"):
                    card_to_move = st.session_state.board_data[col_name].pop(i)
                    st.session_state.board_data[target_column].append(card_to_move)
                    handler.update_board(
                        st.session_state.table,
                        st.session_state.board_id,
                        {
                            "Task": st.session_state.board_data["Tasks"],
                            "In Progress": st.session_state.board_data["In Progress"],
                            "Done": st.session_state.board_data["Done"],
                            "BrainStorm": st.session_state.board_data["BrainStorm"],
                        },
                    )
                    st.experimental_rerun()

            st.markdown("---")
            # Add a new card to the column
            new_card = st.text_input("New card", key=f"new_card_{col_name}")
            if st.button("Add Card", key=f"add_card_{col_name}"):
                if new_card.strip() != "":
                    st.session_state.board_data[col_name].append(new_card)
                    handler.update_board(
                        st.session_state.table,
                        st.session_state.board_id,
                        {
                            "Task": st.session_state.board_data["Tasks"],
                            "In Progress": st.session_state.board_data["In Progress"],
                            "Done": st.session_state.board_data["Done"],
                            "BrainStorm": st.session_state.board_data["BrainStorm"],
                        },
                    )
                    st.experimental_rerun()
                else:
                    st.error("Card content cannot be empty.")
