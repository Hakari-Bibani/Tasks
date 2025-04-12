# handle.py
import uuid
import psycopg2
from psycopg2 import sql
import streamlit as st

# Use caching so the connection is reused between Streamlit reruns.
@st.cache_resource
def get_connection():
    conn_str = st.secrets["postgres"]["connection_string"]
    conn = psycopg2.connect(conn_str)
    return conn

def add_task(category, text):
    """Insert a new task into the table, populating the column corresponding to the category."""
    conn = get_connection()
    cur = conn.cursor()
    new_id = str(uuid.uuid4())
    # Prepare a dict of columns; only the chosen category will get the text.
    columns = {"Task": None, "In Progress": None, "Done": None, "BrainStorm": None}
    if category in columns:
        columns[category] = text
    else:
        raise ValueError("Invalid category")
    # Build the INSERT statement.
    # Because "In Progress" contains a space, we use psycopg2.sql to safely insert the identifier.
    query = sql.SQL("""
        INSERT INTO table1 (id, Task, {in_progress}, Done, BrainStorm)
        VALUES (%s, %s, %s, %s, %s)
    """).format(in_progress=sql.Identifier("In Progress"))
    cur.execute(query, (new_id, columns["Task"], columns["In Progress"], columns["Done"], columns["BrainStorm"]))
    conn.commit()
    cur.close()

def get_tasks():
    """Retrieve all tasks from the table and return them as a list of dictionaries.
       Each dictionary has keys: id, category, and text.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, Task, "In Progress", Done, BrainStorm FROM table1')
    rows = cur.fetchall()
    tasks = []
    for row in rows:
        task_id, task, in_progress, done, brainstorm = row
        if task is not None:
            tasks.append({"id": task_id, "category": "Task", "text": task})
        elif in_progress is not None:
            tasks.append({"id": task_id, "category": "In Progress", "text": in_progress})
        elif done is not None:
            tasks.append({"id": task_id, "category": "Done", "text": done})
        elif brainstorm is not None:
            tasks.append({"id": task_id, "category": "BrainStorm", "text": brainstorm})
    cur.close()
    return tasks

def update_task_category(task_id, new_category):
    """Move a task from its current category to a new category.
       The task’s text is copied to the new category column and removed from the old one.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Retrieve the row to know from which column the text should be moved.
    cur.execute('SELECT Task, "In Progress", Done, BrainStorm FROM table1 WHERE id = %s', (task_id,))
    row = cur.fetchone()
    if row:
        current_text = None
        current_category = None
        if row[0] is not None:
            current_text = row[0]
            current_category = "Task"
        elif row[1] is not None:
            current_text = row[1]
            current_category = "In Progress"
        elif row[2] is not None:
            current_text = row[2]
            current_category = "Done"
        elif row[3] is not None:
            current_text = row[3]
            current_category = "BrainStorm"
        else:
            st.error("Task not found in any category.")
            return
        # Update the task: move the text to new_category and nullify the old column.
        query = sql.SQL("""
            UPDATE table1
            SET {new_col} = %s, {old_col} = NULL
            WHERE id = %s
        """).format(
            new_col=sql.Identifier(new_category),
            old_col=sql.Identifier(current_category)
        )
        cur.execute(query, (current_text, task_id))
        conn.commit()
    cur.close()

def delete_task(task_id):
    """Delete a task from the table."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM table1 WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
