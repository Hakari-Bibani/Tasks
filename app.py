import streamlit as st
import json
from auth import setup_auth, display_auth
from db import get_all_items, add_item, move_item, delete_item
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

# Setup authentication
authenticator = setup_auth()

# Main app function
def main():
    # Display authentication
    if not display_auth(authenticator):
        return
    
    st.title("Kanban Board")
    
    # Initialize session state for items if not present
    if 'items' not in st.session_state:
        st.session_state.items = get_all_items()
    
    # Add refresh button
    if st.button("↻ Refresh Board"):
        st.session_state.items = get_all_items()
        st.rerun()
    
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
                        st.markdown(f'<div class="kanban-card" id="{item["id"]}" draggable="true" ondragstart="drag(event)">{item["text"]}</div>', unsafe_allow_html=True)
                    with col2:
                        if st.button("✖", key=f"delete_{item_key}"):
                            delete_item(item['id'])
                            st.session_state.items = get_all_items()
                            st.rerun()
            
            # Add new item input for each column
            new_item = st.text_area(f"Add to {column_name}", key=f"new_{column_name}", placeholder="Type here...", height=100)
            if st.button(f"Add Item", key=f"add_{column_name}"):
                if new_item.strip():
                    add_item(column_name, new_item)
                    st.session_state.items = get_all_items()
                    st.rerun()

    # Add JavaScript for drag and drop functionality
    st.markdown("""
    <script>
    function allowDrop(ev) {
        ev.preventDefault();
    }

    function drag(ev) {
        ev.dataTransfer.setData("text", ev.target.id);
        ev.dataTransfer.setData("sourceColumn", ev.target.closest(".stColumn").querySelector(".kanban-header").innerText);
    }

    function drop(ev) {
        ev.preventDefault();
        var data = ev.dataTransfer.getData("text");
        var sourceColumn = ev.dataTransfer.getData("sourceColumn");
        var targetColumn = ev.target.closest(".stColumn").querySelector(".kanban-header").innerText;
        
        if (sourceColumn !== targetColumn) {
            // Get the item text
            var itemText = document.getElementById(data).innerText;
            
            // Send data to Streamlit
            const itemData = {
                id: data,
                from_column: sourceColumn,
                to_column: targetColumn,
                text: itemText
            };

            // Use Streamlit's message passing to communicate with Python
            window.parent.postMessage({
                type: "streamlit:moveItem",
                data: itemData
            }, "*");
        }
    }

    // Add event listeners to columns
    document.addEventListener("DOMContentLoaded", function() {
        const columns = document.querySelectorAll(".stColumn");
        columns.forEach(col => {
            col.addEventListener("dragover", allowDrop);
            col.addEventListener("drop", drop);
        });
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Listen for custom events from JavaScript
    if st.session_state.get('moveItemEvent'):
        item_data = st.session_state.moveItemEvent
        move_item(item_data['id'], item_data['from_column'], item_data['to_column'], item_data['text'])
        st.session_state.items = get_all_items()
        st.session_state.moveItemEvent = None
        st.rerun()

    # Custom component to handle JavaScript events
    components.html(
        """
        <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'streamlit:moveItem') {
                const itemData = event.data.data;
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    componentValue: itemData,
                    key: 'moveItemEvent'
                }, '*');
            }
        });
        </script>
        """,
        height=0
    )

if __name__ == "__main__":
    import streamlit.components.v1 as components
    main()
