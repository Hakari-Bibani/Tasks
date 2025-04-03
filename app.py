import streamlit as st
import pandas as pd
import uuid
from handler import DatabaseHandler
import streamlit.components.v1 as components
import os

# Set page configuration
st.set_page_config(
    page_title="Task Board Manager",
    page_icon="📋",
    layout="wide",
)

# Initialize database handler
db_handler = None

# Custom CSS for styling
st.markdown("""
<style>
    .card {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        background-color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        position: relative;
    }
    .column {
        background-color: #f5f5f5;
        border-radius: 5px;
        padding: 10px;
        min-height: 400px;
    }
    .delete-btn {
        position: absolute;
        top: 5px;
        right: 5px;
        cursor: pointer;
        color: #FF5252;
    }
    .board-selector {
        max-width: 300px;
        margin-bottom: 20px;
    }
    .header {
        text-align: center;
        padding: 10px;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px 5px 0 0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Connect to database
def initialize_db():
    global db_handler
    
    # Get database URL from secrets
    if 'db_url' in st.secrets:
        db_url = st.secrets['db_url']
    else:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            db_url = st.text_input("Enter database URL:", type="password", 
                                  help="Example: postgresql://user:password@host/dbname?sslmode=require")
            if not db_url:
                st.warning("Please provide a database URL to continue.")
                return False
    
    try:
        db_handler = DatabaseHandler(db_url)
        return True
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return False

# Generate draggable card component
def create_draggable_card(item_id, content, column, board_table):
    card_html = f"""
    <div class="card" draggable="true" ondragstart="dragStart(event, '{item_id}')">
        <div class="delete-btn" onclick="confirmDelete('{item_id}')">🗑️</div>
        {content}
    </div>
    """
    return card_html

# Create JavaScript for drag and drop functionality
def get_drag_drop_script():
    return """
    <script>
        function dragStart(event, id) {
            event.dataTransfer.setData("text/plain", id);
        }
        
        function allowDrop(event) {
            event.preventDefault();
        }
        
        function drop(event, target_column) {
            event.preventDefault();
            const id = event.dataTransfer.getData("text/plain");
            const data = {
                id: id,
                target_column: target_column
            };
            
            // Send data to Streamlit via component communication
            window.parent.postMessage({
                type: "card_dropped",
                data: data
            }, "*");
        }
        
        function confirmDelete(id) {
            if (confirm("Are you sure you want to delete this card?")) {
                window.parent.postMessage({
                    type: "delete_card",
                    data: { id: id }
                }, "*");
            }
        }
    </script>
    """

# Create a new board
def create_new_board():
    global db_handler

    if st.session_state.new_board_name:
        # Get selected table
        table_name = st.session_state.selected_table
        
        if table_name:
            # Check if table exists and is accessible
            if db_handler.check_table_exists(table_name):
                st.session_state.boards[st.session_state.new_board_name] = table_name
                st.session_state.selected_board = st.session_state.new_board_name
                st.session_state.new_board_name = ""
                st.success(f"Board '{st.session_state.selected_board}' created successfully!")
            else:
                st.error(f"Table '{table_name}' does not exist or is not accessible.")
        else:
            st.error("Please select a table for the board.")
    else:
        st.error("Please enter a board name.")

# Main application
def main():
    if not initialize_db():
        return
    
    # Initialize session state
    if 'boards' not in st.session_state:
        st.session_state.boards = {}
    
    if 'selected_board' not in st.session_state:
        st.session_state.selected_board = None
    
    if 'new_board_name' not in st.session_state:
        st.session_state.new_board_name = ""
    
    # Header
    st.title("Task Board Manager")
    
    # Create new board interface
    with st.expander("Create New Board"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.text_input("Board Name", key="new_board_name")
            
            # Get available tables
            available_tables = db_handler.get_available_tables()
            st.session_state.selected_table = st.selectbox(
                "Select Table", 
                options=available_tables,
                key="selected_table"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Board"):
                create_new_board()
    
    # Board selection
    if st.session_state.boards:
        st.markdown("### Select Board")
        board_options = list(st.session_state.boards.keys())
        selected_board = st.selectbox(
            "Choose a board", 
            options=board_options,
            key="board_selector"
        )
        
        if selected_board != st.session_state.selected_board:
            st.session_state.selected_board = selected_board
    
    # Display the selected board
    if st.session_state.selected_board:
        display_board(st.session_state.selected_board, st.session_state.boards[st.session_state.selected_board])
    else:
        st.info("Please create or select a board to continue.")

# Display board with columns and cards
def display_board(board_name, table_name):
    st.markdown(f"## {board_name}")
    
    # Get data from the database
    data = db_handler.get_all_tasks(table_name)
    
    # Create columns
    col1, col2, col3, col4 = st.columns(4)
    
    # Set up column headers
    col1.markdown('<div class="header">Tasks</div>', unsafe_allow_html=True)
    col2.markdown('<div class="header">In Progress</div>', unsafe_allow_html=True)
    col3.markdown('<div class="header">Done</div>', unsafe_allow_html=True)
    col4.markdown('<div class="header">BrainStorm</div>', unsafe_allow_html=True)
    
    # Add card functionality
    with col1:
        new_task = st.text_area("Add new task", key="new_task", placeholder="Enter task description...")
        if st.button("Add Task"):
            if new_task:
                new_id = str(uuid.uuid4())
                db_handler.add_task(table_name, new_id, new_task)
                st.experimental_rerun()
    
    # Display JavaScript for drag-and-drop
    js_code = get_drag_drop_script()
    components.html(js_code, height=0)
    
    # Handle drag-and-drop events
    card_dropped = get_card_dropped_message()
    if card_dropped:
        card_id = card_dropped["id"]
        target_column = card_dropped["target_column"]
        db_handler.move_task(table_name, card_id, target_column)
        st.experimental_rerun()
    
    # Handle delete card events
    delete_card = get_delete_card_message()
    if delete_card:
        card_id = delete_card["id"]
        db_handler.delete_task(table_name, card_id)
        st.experimental_rerun()
    
    # Display tasks in columns
    with col1:
        st.markdown('<div class="column" ondragover="allowDrop(event)" ondrop="drop(event, \'Task\')">', unsafe_allow_html=True)
        for item in data:
            if item["Task"]:
                st.markdown(create_draggable_card(item["id"], item["Task"], "Task", table_name), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="column" ondragover="allowDrop(event)" ondrop="drop(event, \'In Progress\')">', unsafe_allow_html=True)
        for item in data:
            if item["In Progress"]:
                st.markdown(create_draggable_card(item["id"], item["In Progress"], "In Progress", table_name), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="column" ondragover="allowDrop(event)" ondrop="drop(event, \'Done\')">', unsafe_allow_html=True)
        for item in data:
            if item["Done"]:
                st.markdown(create_draggable_card(item["id"], item["Done"], "Done", table_name), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="column" ondragover="allowDrop(event)" ondrop="drop(event, \'BrainStorm\')">', unsafe_allow_html=True)
        for item in data:
            if item["BrainStorm"]:
                st.markdown(create_draggable_card(item["id"], item["BrainStorm"], "BrainStorm", table_name), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Get custom messages from frontend
def get_card_dropped_message():
    if "card_dropped" in st.session_state:
        data = st.session_state.card_dropped
        del st.session_state.card_dropped
        return data
    return None

def get_delete_card_message():
    if "delete_card" in st.session_state:
        data = st.session_state.delete_card
        del st.session_state.delete_card
        return data
    return None

# Initialize component communication
components.html(
    """
    <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'card_dropped') {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: event.data.data,
                    key: 'card_dropped'
                }, '*');
            }
            else if (event.data.type === 'delete_card') {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: event.data.data,
                    key: 'delete_card'
                }, '*');
            }
        });
    </script>
    """,
    height=0
)

if __name__ == "__main__":
    main()
