import streamlit as st
import psycopg2
import json

# --- Database Connection ---
# (Use your connection string; ensure you protect credentials in production!)
conn = psycopg2.connect(
    "postgresql://neondb_owner:npg_vJSrcVfZ7N6a@ep-snowy-bar-a5zv1qhw-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
)
cur = conn.cursor()

# --- Board (Table) Selection ---
board = st.sidebar.selectbox("Select Board", ["table1", "table2", "table3", "table4", "table5", "table6"])

# For simplicity, we assume each board has a single row with id='board'
def load_board_data(table):
    cur.execute(f"SELECT * FROM {table} WHERE id = 'board'")
    row = cur.fetchone()
    if row:
        # Assume row columns are: id, Task, In Progress, Done, BrainStorm
        return {
            "Task": json.loads(row[1]) if row[1] else [],
            "In Progress": json.loads(row[2]) if row[2] else [],
            "Done": json.loads(row[3]) if row[3] else [],
            "BrainStorm": json.loads(row[4]) if row[4] else [],
        }
    else:
        # If no row exists, create a new one with empty lists
        empty_data = {"Task": [], "In Progress": [], "Done": [], "BrainStorm": []}
        cur.execute(
            f"INSERT INTO {table} (id, \"Task\", \"In Progress\", \"Done\", \"BrainStorm\") VALUES ('board', %s, %s, %s, %s)",
            (json.dumps(empty_data["Task"]), json.dumps(empty_data["In Progress"]),
             json.dumps(empty_data["Done"]), json.dumps(empty_data["BrainStorm"]))
        )
        conn.commit()
        return empty_data

board_data = load_board_data(board)

# --- Helper Function to Save Data ---
def save_board_data(table, data):
    cur.execute(
        f"""UPDATE {table} 
            SET "Task" = %s, "In Progress" = %s, "Done" = %s, "BrainStorm" = %s
            WHERE id = 'board'""",
        (json.dumps(data["Task"]), json.dumps(data["In Progress"]),
         json.dumps(data["Done"]), json.dumps(data["BrainStorm"]))
    )
    conn.commit()

# --- Display Columns & Cards ---
st.write("## Task Board")

# Create four columns for each status
col1, col2, col3, col4 = st.columns(4)
columns = {
    "Task": col1,
    "In Progress": col2,
    "Done": col3,
    "BrainStorm": col4
}

# For each status, display cards.
# In a real app, you’d integrate a drag-and-drop component here.
for status, col in columns.items():
    with col:
        st.subheader(status)
        # Display each card in a container so you can later add drag-and-drop functionality.
        # We use the index as part of the key.
        for idx, card_text in enumerate(board_data[status]):
            # Editable text area for the card
            new_text = st.text_area(
                label=f"{status} Card {idx+1}", 
                value=card_text, 
                key=f"{status}_{idx}"
            )
            # If text changed, update our local board data
            if new_text != card_text:
                board_data[status][idx] = new_text
            # Delete button for the card
            if st.button("🗑️", key=f"del_{status}_{idx}"):
                board_data[status].pop(idx)
                st.experimental_rerun()  # refresh the app to reflect deletion

# --- Placeholder for Drag-and-Drop ---
st.info("Drag-and-drop functionality is not built-in. To enable this, consider integrating a custom Streamlit component (e.g., one that wraps SortableJS or use streamlit-sortable).")

# --- Save Button ---
if st.button("Save Changes"):
    save_board_data(board, board_data)
    st.success("Board updated!")
