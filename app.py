import streamlit as st
import streamlit.components.v1 as components
from sidebar import display_sidebar
from handle import get_cards, add_card
import uuid

st.set_page_config(page_title="Kanban Board", layout="wide")

# Render the sidebar and get the selected board/table name
selected_table = display_sidebar()

st.title(f"Board: {selected_table}")

# Load current cards from the selected table
cards = get_cards(selected_table)

# Create four columns for the board
col_task, col_inprogress, col_done, col_brainstorm = st.columns(4)

def render_cards(status, container):
    container.subheader(status)
    # Display cards for the given status
    for card in cards.get(status, []):
        container.markdown(f"**{card['content']}**")
    # Provide a way to add a new card
    with container.expander(f"Add new card to {status}"):
        new_content = st.text_input(f"New card for {status}", key=f"{status}_new")
        if st.button("Add Card", key=f"btn_{status}"):
            if new_content:
                card_id = str(uuid.uuid4())
                add_card(selected_table, status, card_id, new_content)
                st.experimental_rerun()  # Refresh the app to show the new card

# Render cards in each column
for status, col in zip(["Task", "In Progress", "Done", "Brain Storm"],
                         [col_task, col_inprogress, col_done, col_brainstorm]):
    render_cards(status, col)

# --- Drag & Drop Demo Section (Static Example) ---
components.html(
    """
    <html>
      <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Sortable/1.14.0/Sortable.min.js"></script>
        <style>
          .board { display: flex; justify-content: space-between; }
          .column { width: 22%; min-height: 300px; margin: 10px; border: 1px solid #ccc; padding: 10px; }
          .card { background: #f0f0f0; padding: 8px; margin: 5px 0; cursor: move; }
          h3 { text-align: center; }
        </style>
      </head>
      <body>
        <div class="board">
          <div class="column" id="task">
            <h3>Task</h3>
            <div id="task-list">
              <div class="card">Example Task</div>
            </div>
          </div>
          <div class="column" id="inprogress">
            <h3>In Progress</h3>
            <div id="inprogress-list">
              <div class="card">Example In Progress</div>
            </div>
          </div>
          <div class="column" id="done">
            <h3>Done</h3>
            <div id="done-list">
              <div class="card">Example Done</div>
            </div>
          </div>
          <div class="column" id="brainstorm">
            <h3>Brain Storm</h3>
            <div id="brainstorm-list">
              <div class="card">Example Brain Storm</div>
            </div>
          </div>
        </div>
        <script>
          // Initialize SortableJS for each column list (this is just a demo)
          ['task-list', 'inprogress-list', 'done-list', 'brainstorm-list'].forEach(function(id) {
              new Sortable(document.getElementById(id), {
                  group: 'shared',
                  animation: 150,
                  onEnd: function (evt) {
                    console.log('Moved card from', evt.from.id, 'to', evt.to.id);
                  }
              });
          });
        </script>
      </body>
    </html>
    """,
    height=400,
)
