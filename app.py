import streamlit as st
import psycopg2
import uuid
import time

# Configure the page
st.set_page_config(page_title="Kanban Board", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
.kanban-column {
    background-color: #f1f3f5;
    border-radius: 8px;
    padding: 16px;
    height: 100%;
}
.kanban-card {
    background-color: white;
    border-radius: 4px;
    padding: 8px;
    margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    cursor: grab;
}
.kanban-header {
    font-weight: bold;
    margin-bottom: 16px;
    text-align: center;
    padding: 8px;
    background-color: #4e73df;
    color: white;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# Database connection
def get_connection():
    # Get database credentials from secrets
    conn_string = st.secrets["postgres_connection"]
    return psycopg2.connect(conn_string)

# Get all items from the database
def get_all_items():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, "Task", "In Progress", "Done", "BrainStorm" FROM table1')
        items = cur.fetchall()
        cur.close()
        conn.close()
        
        # Organize items by category
        tasks = []
        in_progress = []
        done = []
        brainstorm = []
        
        for item in items:
            item_id = item[0]
            if item[1]:  # Task
                tasks.append({"id": item_id, "text": item[1]})
            if item[2]:  # In Progress
                in_progress.append({"id": item_id, "text": item[2]})
            if item[3]:  # Done
                done.append({"id": item_id, "text": item[3]})
            if item[4]:  # BrainStorm
                brainstorm.append({"id": item_id, "text": item[4]})
        
        return {
            "Task": tasks,
            "In Progress": in_progress,
            "Done": done,
            "BrainStorm": brainstorm
        }
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return {
            "Task": [],
            "In Progress": [],
            "Done": [],
            "BrainStorm": []
        }

# Add a new item
def add_item(column, text):
    try:
        conn = get_connection()
        cur = conn.cursor()
        item_id = str(uuid.uuid4())
        
        # Create a dictionary with all columns set to None
        item_data = {
            "Task": None,
            "In Progress": None,
            "Done": None,
            "BrainStorm": None
        }
        
        # Set the specified column to the text
        item_data[column] = text
        
        # Insert into database
        cur.execute(
            'INSERT INTO table1 (id, "Task", "In Progress", "Done", "BrainStorm") VALUES (%s, %s, %s, %s, %s)',
            (item_id, item_data["Task"], item_data["In Progress"], item_data["Done"], item_data["BrainStorm"])
        )
        
        conn.commit()
        cur.close()
        conn.close()
        return item_id
    except Exception as e:
        st.error(f"Error adding item: {e}")
        return None

# Update an item when moved to a different column
def move_item(item_id, from_column, to_column, text):
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # First, get the current item
        cur.execute(f'SELECT id, "Task", "In Progress", "Done", "BrainStorm" FROM table1 WHERE id = %s', (item_id,))
        item = cur.fetchone()
        
        if item:
            # Update the item: clear the old column and set the new column
            update_query = f'UPDATE table1 SET "{from_column}" = NULL, "{to_column}" = %s WHERE id = %s'
            cur.execute(update_query, (text, item_id))
            conn.commit()
        
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Error moving item: {e}")

# Delete an item
def delete_item(item_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM table1 WHERE id = %s", (item_id,))
        conn.commit()
        
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Error deleting item: {e}")

# Simple password protection
def password_protection():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        st.title("Kanban Board Login")
        password = st.text_input("Enter password", type="password")
        if st.button("Login"):
            if password == st.secrets["password"]:
                st.session_state.authenticated = True
                st.experimental_rerun()
            else:
                st.error("Incorrect password")
        return False
    return True

# Main app function
def main():
    if not password_protection():
        return
        
    st.title("Kanban Board")
    
    # Initialize session state for items if not present
    if 'items' not in st.session_state:
        st.session_state.items = get_all_items()
    
    # Add refresh button
    if st.button("↻ Refresh Board"):
        st.session_state.items = get_all_items()
        st.experimental_rerun()
    
    # Create columns for the kanban board
    columns = ["Task", "In Progress", "Done", "BrainStorm"]
    cols = st.columns(4)
    
    # Display each column
    for i, column_name in enumerate(columns):
        with cols[i]:
            st.markdown(f'<div class="kanban-header">{column_name}</div>', unsafe_allow_html=True)
            
            # Display existing items
            for item in st.session_state.items[column_name]:
                # Create a unique key for each item
                item_key = f"{column_name}_{item['id']}"
                
                # Create a container for the item
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        # Display the card with drag functionality
                        st.markdown(f'<div class="kanban-card" draggable="true" data-id="{item["id"]}" data-column="{column_name}">{item["text"]}</div>', unsafe_allow_html=True)
                    with col2:
                        if st.button("✖", key=f"delete_{item_key}"):
                            delete_item(item['id'])
                            st.session_state.items = get_all_items()
                            st.experimental_rerun()
            
            # Add new item input for each column
            new_item = st.text_area(f"Add to {column_name}", key=f"new_{column_name}", placeholder="Type here...", height=100)
            if st.button(f"Add Item", key=f"add_{column_name}"):
                if new_item.strip():
                    add_item(column_name, new_item)
                    st.session_state.items = get_all_items()
                    st.experimental_rerun()
    
    # Add functionality to handle drag and drop
    st.markdown("""
    <script>
    // Drag and drop functionality
    document.addEventListener('DOMContentLoaded', function() {
        const cards = document.querySelectorAll('.kanban-card');
        const columns = document.querySelectorAll('.stColumn');
        
        // Add drag event listeners to cards
        cards.forEach(card => {
            card.addEventListener('dragstart', function(e) {
                e.dataTransfer.setData('text/plain', JSON.stringify({
                    id: this.dataset.id,
                    text: this.textContent,
                    fromColumn: this.dataset.column
                }));
            });
        });
        
        // Add drop event listeners to columns
        columns.forEach(column => {
            column.addEventListener('dragover', function(e) {
                e.preventDefault();
            });
            
            column.addEventListener('drop', function(e) {
                e.preventDefault();
                const data = JSON.parse(e.dataTransfer.getData('text/plain'));
                const toColumn = this.querySelector('.kanban-header').textContent;
                
                if (data.fromColumn !== toColumn) {
                    // Send to Streamlit via session_state
                    const moveData = {
                        id: data.id,
                        from_column: data.fromColumn,
                        to_column: toColumn,
                        text: data.text
                    };
                    
                    // This function will communicate with Streamlit
                    window.parent.postMessage({
                        type: 'streamlit:moveItem',
                        data: moveData
                    }, '*');
                }
            });
        });
    });
    </script>
    """, unsafe_allow_html=True)

    # Handle the move action with a callback
    if st.session_state.get('moveItemData'):
        data = st.session_state.moveItemData
        move_item(data['id'], data['from_column'], data['to_column'], data['text'])
        st.session_state.items = get_all_items()
        del st.session_state.moveItemData
        st.experimental_rerun()
        
    # Component to handle the JavaScript bridge
    import streamlit.components.v1 as components
    components.html("""
    <script>
    // Handle messages from the parent window
    window.addEventListener('message', function(e) {
        if (e.data.type === 'streamlit:moveItem') {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: e.data.data,
                key: 'moveItemData'
            }, '*');
        }
    });
    </script>
    """, height=0)

if __name__ == "__main__":
    main()
