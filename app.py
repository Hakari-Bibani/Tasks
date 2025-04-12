import streamlit as st
import psycopg2
import uuid

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

# Database connection string
DB_CONNECTION = "postgresql://neondb_owner:npg_vJSrcVfZ7N6a@ep-snowy-bar-a5zv1qhw-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Database connection
def get_connection():
    return psycopg2.connect(DB_CONNECTION)

# Get all items from the database
def get_all_items():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, "Task", "In Progress", "Done", "BrainStorm" FROM table1')
        items = cur.fetchall()
        cur.close()
        conn.close()
        
        # Initialize empty lists for each category
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

# Initialize session state
def init_session_state():
    if 'items' not in st.session_state:
        st.session_state['items'] = get_all_items()

# Main app function
def main():
    st.title("Kanban Board")
    
    # Initialize session state
    init_session_state()
    
    # Add refresh button
    if st.button("↻ Refresh Board"):
        st.session_state['items'] = get_all_items()
        st.rerun()
    
    # Create columns for the kanban board
    columns = ["Task", "In Progress", "Done", "BrainStorm"]
    cols = st.columns(4)
    
    # Display each column
    for i, column_name in enumerate(columns):
        with cols[i]:
            st.markdown(f'<div class="kanban-header">{column_name}</div>', unsafe_allow_html=True)
            
            # Make sure the column exists in session state items
            items_in_column = st.session_state['items'].get(column_name, [])
            
            # Display existing items
            for item in items_in_column:
                # Create a unique key for each item
                item_key = f"{column_name}_{item['id']}"
                
                # Create a container for the item
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f'''
                        <div class="kanban-card" 
                             draggable="true" 
                             data-id="{item["id"]}" 
                             data-column="{column_name}">
                            {item["text"]}
                        </div>
                        ''', unsafe_allow_html=True)
                    with col2:
                        if st.button("✖", key=f"delete_{item_key}"):
                            delete_item(item['id'])
                            st.session_state['items'] = get_all_items()
                            st.rerun()
            
            # Add new item input for each column
            new_item = st.text_area(f"Add to {column_name}", key=f"new_{column_name}", placeholder="Type here...", height=100)
            if st.button(f"Add Item", key=f"add_{column_name}"):
                if new_item.strip():
                    add_item(column_name, new_item)
                    st.session_state['items'] = get_all_items()
                    st.rerun()
    
    # Add drag-and-drop functionality
    st.components.v1.html("""
    <script>
    // Function to set up drag and drop
    function setupDragAndDrop() {
        console.log("Setting up drag and drop");
        const cards = document.querySelectorAll('.kanban-card');
        const columns = document.querySelectorAll('.stColumn');
        
        cards.forEach(card => {
            card.addEventListener('dragstart', function(e) {
                console.log("Drag started", this.dataset.id);
                e.dataTransfer.setData('text/plain', JSON.stringify({
                    id: this.dataset.id,
                    text: this.textContent.trim(),
                    fromColumn: this.dataset.column
                }));
            });
        });
        
        columns.forEach(column => {
            column.addEventListener('dragover', function(e) {
                e.preventDefault();
            });
            
            column.addEventListener('drop', function(e) {
                e.preventDefault();
                console.log("Drop event triggered");
                
                try {
                    const data = JSON.parse(e.dataTransfer.getData('text/plain'));
                    const headerElement = this.querySelector('.kanban-header');
                    if (!headerElement) return;
                    
                    const toColumn = headerElement.textContent.trim();
                    console.log("Moving from", data.fromColumn, "to", toColumn);
                    
                    if (data.fromColumn !== toColumn) {
                        // Use Streamlit's component communication
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: {
                                id: data.id,
                                from_column: data.fromColumn,
                                to_column: toColumn,
                                text: data.text
                            },
                            key: 'move_item_data'
                        }, '*');
                    }
                } catch (error) {
                    console.error('Error in drop handler:', error);
                }
            });
        });
    }

    // Run setup when DOM is fully loaded and again after a small delay
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(setupDragAndDrop, 1000);
    });

    // Also run setup now in case DOM is already loaded
    setTimeout(setupDragAndDrop, 1000);
    </script>
    """, height=0)
    
    # Process move item requests
    if 'move_item_data' in st.session_state:
        data = st.session_state.move_item_data
        move_item(data['id'], data['from_column'], data['to_column'], data['text'])
        st.session_state['items'] = get_all_items()
        del st.session_state.move_item_data
        st.rerun()

if __name__ == "__main__":
    main()
