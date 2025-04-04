import streamlit as st
from handlers import *
from sidebar import show_sidebar
import json

st.set_page_config(layout="wide", page_title="Kanban Board")

# Initialize session state
if 'current_board' not in st.session_state:
    st.session_state.current_board = "table1"

# Load CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Show sidebar
show_sidebar()

# Main board columns
columns = ["Task", "In Progress", "Done", "BrainStorm"]
board_cols = st.columns(4)

for col_idx, (col, column_name) in enumerate(zip(board_cols, columns)):
    with col:
        st.subheader(column_name)
        tasks = get_tasks(st.session_state.current_board, column_name)
        
        # Add task button
        if st.button(f"➕ Add Task", key=f"add_{column_name}"):
            add_task(st.session_state.current_board, column_name, "New Task")
            st.rerun()
        
        # Display tasks
        for task in tasks:
            with st.container():
                st.markdown(
                    f"""
                    <div class="kanban-card" draggable="true" 
                        data-task='{json.dumps(task)}'
                        data-column="{column_name}"
                        id="{task['id']}">
                        {task['content']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# Drag and drop handling
if st.query_params.get("drag_data"):
    drag_data = json.loads(st.query_params["drag_data"][0])
    move_task(
        st.session_state.current_board,
        drag_data["task_id"],
        drag_data["old_column"],
        drag_data["new_column"]
    )
    st.query_params.clear()
    st.rerun()

# Drag and drop JavaScript
st.components.v1.html("""
<script>
document.addEventListener('dragstart', (e) => {
    if (e.target.classList.contains('kanban-card')) {
        const taskData =
