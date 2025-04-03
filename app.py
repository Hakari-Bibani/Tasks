import streamlit as st
import json
from handle import get_connection

# --- Establish Database Connection ---
conn = get_connection()
cur = conn.cursor()

# --- Database Helper Functions ---
def load_board_data(table):
    """
    Load board data from the given table.
    Assumes a row with id 'board' exists; if not, creates one.
    """
    cur.execute(f"SELECT * FROM {table} WHERE id = 'board'")
    row = cur.fetchone()
    if row:
        # Expected row order: id, Task, In Progress, Done, BrainStorm
        return {
            "Task": json.loads(row[1]) if row[1] else [],
            "In Progress": json.loads(row[2]) if row[2] else [],
            "Done": json.loads(row[3]) if row[3] else [],
            "BrainStorm": json.loads(row[4]) if row[4] else [],
        }
    else:
        empty_data = {"Task": [], "In Progress": [], "Done": [], "BrainStorm": []}
        cur.execute(
            f"""INSERT INTO {table} (id, "Task", "In Progress", "Done", "BrainStorm")
                VALUES ('board', %s, %s, %s, %s)""",
            (json.dumps(empty_data["Task"]), json.dumps(empty_data["In Progress"]),
             json.dumps(empty_data["Done"]), json.dumps(empty_data["BrainStorm"]))
        )
        conn.commit()
        return empty_data

def save_board_data(table, data):
    """
    Save the board data back to the database.
    """
    cur.execute(
        f"""UPDATE {table} 
            SET "Task" = %s, "In Progress" = %s, "Done" = %s, "BrainStorm" = %s
            WHERE id = 'board'""",
        (json.dumps(data["Task"]), json.dumps(data["In Progress"]),
         json.dumps(data["Done"]), json.dumps(data["BrainStorm"]))
    )
    conn.commit()

# --- Sidebar: Board Selection ---
st.sidebar.title("Task Management Boards")
board = st.sidebar.selectbox("Select Board", ["table1", "table2", "table3", "table4", "table5", "table6"])

# Load board data from the selected table.
board_data = load_board_data(board)

# --- Main App Interface ---
st.title("Task Management Board")
st.write("Edit tasks in each column. (Note: Drag-and-drop functionality requires a custom component.)")

# Create four columns for the main statuses.
col1, col2, col3, col4 = st.columns(4)
columns = {
    "Task": col1,
    "In Progress": col2,
    "Done": col3,
    "BrainStorm": col4
}

# Render each column with its cards.
for status, col in columns.items():
    with col:
        st.subheader(status)
        # Display each card in the current status.
        for idx, card_text in enumerate(board_data[status]):
            new_text = st.text_area(label=f"{status} Card {idx+1}", value=card_text, key=f"{status}_{idx}")
            if new_text != card_text:
                board_data[status][idx] = new_text
            # Delete button for the card.
            if st.button("🗑️", key=f"del_{status}_{idx}"):
                board_data[status].pop(idx)
                st.experimental_rerun()
        # Input to add a new card.
        new_card = st.text_input(f"Add new card to {status}", key=f"new_{status}")
        if st.button(f"Add Card to {status}", key=f"add_{status}"):
            if new_card:
                board_data[status].append(new_card)
                st.experimental_rerun()

# Save changes button.
if st.button("Save Changes"):
    save_board_data(board, board_data)
    st.success("Board updated!")

st.info("Drag-and-drop functionality is not built-in. Consider integrating a custom component (e.g., streamlit-sortable) for that feature.")
