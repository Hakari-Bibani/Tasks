import uuid
import psycopg2
import streamlit as st

# Retrieve the database connection URL from Streamlit secrets
DB_URL = st.secrets["connections"]["neon"]["url"]  # expects secrets.toml with [connections.neon] section

def get_board_data(board_table):
    """Fetch all tasks for the given board (table) and categorize them by column."""
    conn = psycopg2.connect(DB_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute(f'SELECT id, "Task", "In Progress", "Done", "BrainStorm" FROM {board_table};')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Separate tasks by their current column
    tasks, in_progress, done, brainstorm = [], [], [], []
    for (id_val, task, in_prog, done_val, brainstorm_val) in rows:
        if task not in (None, ""):
            tasks.append((id_val, task))
        if in_prog not in (None, ""):
            in_progress.append((id_val, in_prog))
        if done_val not in (None, ""):
            done.append((id_val, done_val))
        if brainstorm_val not in (None, ""):
            brainstorm.append((id_val, brainstorm_val))
    return tasks, in_progress, done, brainstorm

def add_card(board_table, column, content):
    """Add a new task card to the specified column of the board."""
    new_id = str(uuid.uuid4())  # generate a unique ID for the new card
    # Prepare values for each column (only the target column gets the content)
    col_names = ["Task", "In Progress", "Done", "BrainStorm"]
    values = [None, None, None, None]
    if column in col_names:
        values[col_names.index(column)] = content
    else:
        values[0] = content  # default to "Task" if column name is unexpected
    conn = psycopg2.connect(DB_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute(
        f'INSERT INTO {board_table} (id, "Task", "In Progress", "Done", "BrainStorm") VALUES (%s, %s, %s, %s, %s);',
        [new_id] + values
    )
    conn.commit()
    cur.close()
    conn.close()

def move_card(board_table, card_id, from_col, to_col, content):
    """Move an existing card from one column to another by updating its fields."""
    conn = psycopg2.connect(DB_URL, sslmode='require')
    cur = conn.cursor()
    # Set the new column to the content and clear the old column
    query = f'UPDATE {board_table} SET "{to_col}" = %s, "{from_col}" = NULL WHERE id = %s;'
    cur.execute(query, (content, card_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_card(board_table, card_id):
    """Delete a task card from the board."""
    conn = psycopg2.connect(DB_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute(f'DELETE FROM {board_table} WHERE id = %s;', (card_id,))
    conn.commit()
    cur.close()
    conn.close()
