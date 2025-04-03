import psycopg2
import streamlit as st

def get_connection():
    """
    Establish a connection to the PostgreSQL database using the connection string
    stored in Streamlit's secrets.
    """
    connection_url = st.secrets["DATABASE_URL"]
    return psycopg2.connect(connection_url)

def get_tasks(board):
    """
    Retrieve all tasks from the given board (table). 
    Returns a dictionary with keys: 'Task', 'In Progress', 'Done', 'BrainStorm'.
    Each value is a list of tuples (id, content).
    """
    conn = get_connection()
    cur = conn.cursor()
    query = f'SELECT id, Task, "In Progress", Done, BrainStorm FROM {board}'
    cur.execute(query)
    rows = cur.fetchall()
    tasks = {"Task": [], "In Progress": [], "Done": [], "BrainStorm": []}
    for row in rows:
        card_id = row[0]
        # The row should have only one non-null column among the four status columns.
        for col, content in zip(["Task", "In Progress", "Done", "BrainStorm"], row[1:]):
            if content is not None:
                tasks[col].append((card_id, content))
                break
    cur.close()
    conn.close()
    return tasks

def add_task(board, column, card_id, content):
    """
    Add a new card to the specified board and column.
    The card is inserted as a new row with the card content stored in the designated column.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Prepare a list of values for columns: only the specified column gets the content.
    columns = ["Task", "In Progress", "Done", "BrainStorm"]
    values = [None, None, None, None]
    try:
        idx = columns.index(column)
    except ValueError:
        return
    values[idx] = content
    query = f"""INSERT INTO {board} (id, Task, "In Progress", Done, BrainStorm) 
                VALUES (%s, %s, %s, %s, %s)"""
    cur.execute(query, (card_id, values[0], values[1], values[2], values[3]))
    conn.commit()
    cur.close()
    conn.close()

def update_task(board, task_id, new_status):
    """
    Move a card to a new column.
    This function reads the current card to find its content, then updates the row:
    the current status column is set to NULL and the new status column is set to the content.
    """
    conn = get_connection()
    cur = conn.cursor()
    query = f"SELECT * FROM {board} WHERE id = %s"
    cur.execute(query, (task_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return

    # The table columns: id, Task, "In Progress", Done, BrainStorm
    status_columns = ["Task", "In Progress", "Done", "BrainStorm"]
    current_status = None
    content = None
    # Determine which column currently holds the content.
    for i, col in enumerate(status_columns, start=1):
        if row[i] is not None:
            current_status = col
            content = row[i]
            break
    if current_status is None or current_status == new_status:
        cur.close()
        conn.close()
        return

    # Update: clear the old column and set the new column with the content.
    query = f'UPDATE {board} SET "{current_status}" = NULL, "{new_status}" = %s WHERE id = %s'
    cur.execute(query, (content, task_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_task(board, task_id):
    """
    Delete the card (row) from the board with the given task_id.
    """
    conn = get_connection()
    cur = conn.cursor()
    query = f"DELETE FROM {board} WHERE id = %s"
    cur.execute(query, (task_id,))
    conn.commit()
    cur.close()
    conn.close()
