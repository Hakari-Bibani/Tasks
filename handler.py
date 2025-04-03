import streamlit as st
import psycopg2
from uuid import uuid4

def init_db():
    """Initialize the database: create tables for boards and board names if not exist."""
    conn = psycopg2.connect(st.secrets["postgres"]["connection_string"])
    cur = conn.cursor()
    # Create six board tables (table1 ... table6) if they don't exist
    for i in range(1, 7):
        table = f"table{i}"
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {table} (
                id TEXT PRIMARY KEY,
                "Task" TEXT,
                "In Progress" TEXT,
                "Done" TEXT,
                "BrainStorm" TEXT
            );
        ''')
    # Table to store board names
    cur.execute('''
        CREATE TABLE IF NOT EXISTS board_names (
            board_id INT PRIMARY KEY,
            name TEXT
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

def get_board_names():
    """Fetch all board IDs and names from the board_names table."""
    conn = psycopg2.connect(st.secrets["postgres"]["connection_string"])
    cur = conn.cursor()
    cur.execute("SELECT board_id, name FROM board_names ORDER BY board_id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Return a dictionary {board_id: name}
    return {row[0]: row[1] for row in rows}

def create_board(name):
    """Create a new board with the given name. Returns the new board's ID, or None if maxed out."""
    conn = psycopg2.connect(st.secrets["postgres"]["connection_string"])
    cur = conn.cursor()
    # Determine the next available board_id (1-6)
    cur.execute("SELECT board_id FROM board_names;")
    used_ids = {row[0] for row in cur.fetchall()}
    board_id = None
    for i in range(1, 7):
        if i not in used_ids:
            board_id = i
            break
    if board_id is None:
        # All 6 boards are in use
        cur.close()
        conn.close()
        return None
    # Insert the new board record
    cur.execute("INSERT INTO board_names (board_id, name) VALUES (%s, %s);", (board_id, name))
    conn.commit()
    cur.close()
    conn.close()
    return board_id

def fetch_tasks(board_id):
    """Retrieve all tasks for the given board, organized by column."""
    conn = psycopg2.connect(st.secrets["postgres"]["connection_string"])
    cur = conn.cursor()
    table = f"table{board_id}"
    cur.execute(f'SELECT id, "Task", "In Progress", "Done", "BrainStorm" FROM {table};')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    tasks_by_col = {"Task": [], "In Progress": [], "Done": [], "BrainStorm": []}
    for row in rows:
        task_id, task, in_prog, done, brainstorm = row
        # Only one of task, in_prog, done, brainstorm will have content (others are None)
        if task is not None:
            tasks_by_col["Task"].append({"id": task_id, "content": task})
        elif in_prog is not None:
            tasks_by_col["In Progress"].append({"id": task_id, "content": in_prog})
        elif done is not None:
            tasks_by_col["Done"].append({"id": task_id, "content": done})
        elif brainstorm is not None:
            tasks_by_col["BrainStorm"].append({"id": task_id, "content": brainstorm})
    return tasks_by_col

def add_task(board_id, column, content):
    """Insert a new task into the specified board table and column. Returns the new task's id."""
    conn = psycopg2.connect(st.secrets["postgres"]["connection_string"])
    cur = conn.cursor()
    task_id = str(uuid4())
    table = f"table{board_id}"
    # Prepare values for all four status columns
    # Only the target column gets the content; others get NULL
    task_val = content if column == "Task" else None
    prog_val = content if column == "In Progress" else None
    done_val = content if column == "Done" else None
    brain_val = content if column == "BrainStorm" else None
    cur.execute(
        f'INSERT INTO {table} (id, "Task", "In Progress", "Done", "BrainStorm") VALUES (%s, %s, %s, %s, %s);',
        (task_id, task_val, prog_val, done_val, brain_val)
    )
    conn.commit()
    cur.close()
    conn.close()
    return task_id

def delete_task(board_id, task_id):
    """Delete a task from the specified board by its ID."""
    conn = psycopg2.connect(st.secrets["postgres"]["connection_string"])
    cur = conn.cursor()
    table = f"table{board_id}"
    cur.execute(f"DELETE FROM {table} WHERE id = %s;", (task_id,))
    conn.commit()
    cur.close()
    conn.close()

def update_task_status(board_id, task_id, new_column, content):
    """
    Move a task to a new column (status) in the specified board.
    Updates the row so that only the new_column contains the content.
    """
    conn = psycopg2.connect(st.secrets["postgres"]["connection_string"])
    cur = conn.cursor()
    table = f"table{board_id}"
    # Set up values for each column based on the new status
    task_val = content if new_column in ["Task", "task"] else None
    prog_val = content if new_column in ["In Progress", "in-progress"] else None
    done_val = content if new_column in ["Done", "done"] else None
    brain_val = content if new_column in ["BrainStorm", "brainstorm"] else None
    cur.execute(
        f'UPDATE {table} SET "Task"=%s, "In Progress"=%s, "Done"=%s, "BrainStorm"=%s WHERE id=%s;',
        (task_val, prog_val, done_val, brain_val, task_id)
    )
    conn.commit()
    cur.close()
    conn.close()
