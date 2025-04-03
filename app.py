import streamlit as st
import handler as db
from streamlit_sortables import sort_items

# Secure session management
st.set_page_config(
    layout="wide",
    page_title="Secure Kanban Board",
    page_icon="🔒"
)

def initialize_session():
    """Initialize all session state variables securely"""
    if 'boards' not in st.session_state:
        st.session_state.boards = db.get_all_boards()
    if 'current_board' not in st.session_state:
        st.session_state.current_board = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

def auth_gate():
    """Simple authentication gate"""
    if not st.session_state.authenticated:
        with st.container():
            st.title("🔒 Secure Kanban Board")
            password = st.text_input("Enter access password:", type="password")
            if st.button("Login"):
                if db.verify_password(password):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password")
            st.stop()

def display_board(board_name):
    """Secure board display with all features"""
    st.header(f"Board: {board_name}")
    board_data = db.get_board_data(board_name)
    
    # Prepare columns for drag-and-drop
    columns = {
        "Task": {"items": [], "title": "Tasks"},
        "In Progress": {"items": [], "title": "In Progress"},
        "Done": {"items": [], "title": "Done"},
        "BrainStorm": {"items": [], "title": "BrainStorm"}
    }
    
    # Populate with encrypted data
    for _, row in board_data.iterrows():
        for col in columns:
            if row[col]:
                columns[col]["items"].append({
                    "id": row['id'],
                    "content": db.decrypt_data(row[col])
                })
    
    sortable_items = [
        {"header": columns[col]["title"], "items": columns[col]["items"]} 
        for col in columns
    ]
    
    # Secure drag-and-drop handling
    changed = sort_items(sortable_items, multi_containers=True, direction="horizontal")
    
    if changed:
        db.clear_board(board_name)
        for column in changed:
            col_name = column["header"]
            if col_name == "Tasks": col_name = "Task"
            for item in column["items"]:
                db.add_task_to_board(
                    board_name, 
                    item["id"], 
                    db.encrypt_data(item["content"]),  # Encrypt before saving
                    col_name
                )
    
    # Secure task addition
    with st.expander("➕ Add New Task", expanded=False):
        new_task_col = st.selectbox(
            "Column", 
            ["Task", "In Progress", "Done", "BrainStorm"],
            key="new_task_col"
        )
        new_task_content = st.text_area("Task Content", key="new_task_content")
        if st.button("Add Task"):
            if new_task_content:
                db.add_task_to_board(
                    board_name, 
                    db.generate_secure_id(),
                    db.encrypt_data(new_task_content),
                    new_task_col
                )
                st.rerun()

def main():
    initialize_session()
    auth_gate()
    
    st.title("Secure Kanban Board")
    
    # Secure board management sidebar
    with st.sidebar:
        st.header("Board Management")
        
        # Password change option
        if st.button("Change Password"):
            st.session_state.show_password_change = True
            
        if st.session_state.get('show_password_change'):
            new_pass = st.text_input("New Password:", type="password")
            confirm_pass = st.text_input("Confirm Password:", type="password")
            if st.button("Update"):
                if new_pass == confirm_pass:
                    db.update_password(new_pass)
                    st.success("Password updated successfully")
                    st.session_state.show_password_change = False
                else:
                    st.error("Passwords don't match")
            if st.button("Cancel"):
                st.session_state.show_password_change = False
        
        st.divider()
        
        # Board creation
        new_board_name = st.text_input("Create New Board", key="new_board")
        if st.button("Create Board"):
            if new_board_name:
                db.create_board(new_board_name)
                st.session_state.boards = db.get_all_boards()
                st.rerun()
        
        st.divider()
        st.subheader("Your Boards")
        
        # Board selection
        for board in st.session_state.boards:
            if st.button(board, key=f"board_{board}"):
                st.session_state.current_board = board
    
    # Main board display
    if st.session_state.current_board:
        display_board(st.session_state.current_board)
    else:
        st.info("Please select or create a board from the sidebar")

if __name__ == "__main__":
    main()
