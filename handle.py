# handle.py
import psycopg2
import json
import uuid
import streamlit as st

def get_connection():
    # Get the database URL from st.secrets
    DATABASE_URL = st.secrets["DATABASE_URL"]
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def initialize_table():
    """Creates the table and default row if they do not exist."""
    conn = get_connection()
    cur = conn.cursor()
    # Check if table exists; if not, create it.
    cur.execute("SELECT to_regclass('public.table1');")
    if cur.fetchone()[0] is None:
        cur.execute("""
            CREATE TABLE table1 (
                id TEXT PRIMARY KEY,
                Task TEXT,
                "In Progress" TEXT,
                Done TEXT,
                BrainStorm TEXT
            );
        """)
        conn.commit()
        
    # Check if a default row exists; if not, insert one.
    cur.execute("SELECT COUNT(*) FROM table1;")
    count = cur.fetchone()[0]
    if count == 0:
        empty_list = json.dumps([])
        cur.execute(
            "INSERT INTO table1 (id, Task, \"In Progress\", Done, BrainStorm) VALUES (%s, %s, %s, %s, %s);",
            ('default', empty_list, empty_list, empty_list, empty_list)
        )
        conn.commit()
    cur.close()
    conn.close()

def get_tasks(column):
    """Returns the list of tasks for the specified column."""
    conn = get_connection()
    cur = conn.cursor()
    query = f"SELECT {column} FROM table1 WHERE id = 'default';"
    cur.execute(query)
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        try:
            tasks = json.loads(result[0])
        except Exception:
            tasks = []
        return tasks
    return []

def update_tasks(column, tasks):
    """Updates the specified column with a new tasks list."""
    conn = get_connection()
    cur = conn.cursor()
    tasks_json = json.dumps(tasks)
    query = f"UPDATE table1 SET {column} = %s WHERE id = 'default';"
    cur.execute(query, (tasks_json,))
    conn.commit()
    cur.close()
    conn.close()

def add_task(column, task_text):
    """Adds a new task (with a unique id) to the column."""
    tasks = get_tasks(column)
    task = {"id": str(uuid.uuid4()), "text": task_text}
    tasks.append(task)
    update_tasks(column, tasks)

def delete_task(column, task_id):
    """Deletes a task from the column based on its id."""
    tasks = get_tasks(column)
    tasks = [t for t in tasks if t["id"] != task_id]
    update_tasks(column, tasks)

def move_task(source_column, target_column, task_id, new_index):
    """Moves a task from one column to another at the specified position."""
    source_tasks = get_tasks(source_column)
    task = next((t for t in source_tasks if t["id"] == task_id), None)
    if task:
        source_tasks = [t for t in source_tasks if t["id"] != task_id]
        update_tasks(source_column, source_tasks)
        target_tasks = get_tasks(target_column)
        target_tasks.insert(new_index, task)
        update_tasks(target_column, target_tasks)
