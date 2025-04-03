import streamlit as st
import psycopg2
import json

# --- Database Connection ---
# Use Streamlit secrets to keep your credentials secure.
def get_connection():
    # In Streamlit Cloud, add your connection string to the Secrets.
    # For local testing, you can create a .streamlit/secrets.toml file.
    connection_string = st.secrets["DATABASE_URL"] if "DATABASE_URL" in st.secrets else "postgresql://neondb_owner:npg_vJSrcVfZ7N6a@ep-snowy-bar-a5zv1qhw-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
    try:
        conn = psycopg2.connect(connection_string)
        return conn
    except Exception as e:
        st.error("Error connecting to the database:")
        st.error(e)
        st.stop()

conn = get_connection()
cur = conn.cursor()

# --- Database Functions ---
def load_board_data(table):
    """
    Load board data from the given table.
    Each board is stored in a row with id 'board'.
    The columns store serialized JSON lists.
    """
    cur.execute(f"SELECT * FROM {table} WHERE id = 'board'")
    row = cur.fetchone()
    if row:
        # row structure: id, Task, In Progress, Done, BrainStorm
        return {
            "Task": json.loads(row[1]) if row[1] else [],
            "In Progress": json.loads(row[2]) if row[2] else [],
            "Done": json.loads(row[3]) if row[3] else [],
            "BrainStorm": json.loads(row[4]) if row[4] else [],
        }
    else:
        empty_data = {"Task": [], "In Progress": [], "Done": [], "BrainStorm": []}
        cur.execute(
            f"INSERT INTO {table} (id, \"Task\", \"In Progress\", \"Done\", \"BrainStorm\") VALUES ('board', %s, %s, %s, %s)",
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

# --- Streamlit Sidebar ---
st.sidebar.title("Task Management Boards")
# Allow users to select which board (table) to use.
board = st.sidebar.selectbox("Select Board", ["table1", "table2", "table3", "table4", "table5", "table6"])

# Load the board data for the selected table.
board_data = load_board_data(board)

# --- Main App ---
st.title("Task Management Board")
st.write("Edit the tasks in each column. Drag-and-drop functionality is not built-in. To enable that, integrate a custom component (e.g., streamlit-sortable).")

# Create four columns for each status.
col1, col2, col3, col4 = st.columns(4)
columns = {
    "Task": col1,
    "In Progress": col2,
    "Done": col3,
    "BrainStorm": col4
}

# For each column, display its cards.
for status, col in columns.items():
    with col:
        st.subheader(status)
        # Iterate over the list of cards in this status.
        for idx, card_text in enumerate(board_data[status]):
            new_text = st.text_area(label=f"{status} Card {idx+1}", value=card_text, key=f"{status}_{idx}")
            if new_text != card_text:
                board_data[status][idx] = new_text
            # Delete button for each card.
            if st.button("🗑️", key=f"del_{status}_{idx}"):
                board_data[status].pop(idx)
                st.experimental_rerun()
        # Option to add a new card.
        new_card = st.text_input(f"Add new card to {status}", key=f"new_{status}")
        if st.button(f"Add Card to {status}", key=f"add_{status}"):
            if new_card:
                board_data[status].append(new_card)
                st.experimental_rerun()

# Save changes button.
if st.button("Save Changes"):
    save_board_data(board, board_data)
    st.success("Board updated!")

st.info("Note: Drag-and-drop functionality is a placeholder. To enable it, integrate a custom component (e.g., one wrapping SortableJS).")
