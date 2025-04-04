import streamlit as st
from handlers import get_tasks, handle_task_update
from sidebar import show_sidebar
import json

st.set_page_config(layout="wide")

# Initialize session state
if 'current_board' not in st.session_state:
    st.session_state.current_board = "table1"

# Load custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Show sidebar
show_sidebar()

# Main board
st.header(f"Board: {st.session_state.current_board.replace('table', 'Board ')}")

# Create columns
cols = st.columns(4)
columns = ["Task", "In Progress", "Done", "BrainStorm"]

for col, column_name in zip(cols, columns):
    with col:
        st.subheader(column_name)
        tasks = get_tasks(st.session_state.current_board, column_name)
        
        # Add new task button
        if st.button(f"➕ Add Task", key=f"add_{column_name}"):
            handle_task_update(
                board=st.session_state.current_board,
                task_id=f"new_task_{len(tasks)}",
                column=column_name,
                content="New task"
            )
            st.experimental_rerun()
        
        # Tasks container
        with st.container():
            for task in tasks:
                # Draggable card
                st.markdown(f"""
                    <div class="draggable" draggable="true" data-task='{json.dumps(task)}'>
                        <div class="card">
                            <div class="card-content">{task['content']}</div>
                            <div class="card-actions">
                                <button class="edit-btn" onclick="handleEdit('{task['id']}')">Edit</button>
                                <button class="delete-btn" onclick="handleDelete('{task['id']}')">×</button>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# Drag and drop handling
if st.experimental_get_query_params().get('dropped'):
    data = json.loads(st.experimental_get_query_params()['dropped'][0])
    handle_task_update(
        board=st.session_state.current_board,
        task_id=data['taskId'],
        column=data['newColumn']
    )
    st.experimental_rerun()

# JavaScript for drag and drop
st.components.v1.html("""
<script>
document.addEventListener('dragstart', (e) => {
    if (e.target.closest('.draggable')) {
        e.dataTransfer.setData('text/plain', e.target.dataset.task);
    }
});

document.addEventListener('dragover', (e) => {
    e.preventDefault();
});

document.addEventListener('drop', (e) => {
    e.preventDefault();
    const data = JSON.parse(e.dataTransfer.getData('text/plain'));
    const newColumn = e.target.closest('.stContainer')?.querySelector('h3')?.innerText;
    if (newColumn) {
        window.parent.postMessage({
            type: 'dropEvent',
            data: {
                taskId: data.id,
                newColumn: newColumn
            }
        }, '*');
    }
});

window.addEventListener('message', (event) => {
    if (event.data.type === 'dropEvent') {
        const params = new URLSearchParams(window.location.search);
        params.set('dropped', JSON.stringify(event.data.data));
        window.history.replaceState(null, null, `?${params.toString()}`);
        window.location.reload();
    }
});
</script>
""")
