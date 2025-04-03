import psycopg2
import uuid
import streamlit as st

def get_connection():
    # The connection string is stored in Streamlit secrets.
    conn_str = st.secrets["postgresql"]["connection_string"]
    conn = psycopg2.connect(conn_str)
    return conn

def get_tasks(table_name):
    """Fetch all tasks from the given table.
    Assumes that for each row only one of the four board columns is non-null."""
    conn = get_connection()
    cur = conn.cursor()
    query = f'''SELECT id, password, "Task", "In Progress", "Done", "BrainStorm"
                FROM {table_name}'''
    cur.execute(query)
    rows = cur.fetchall()
    tasks = []
    for row in rows:
        task_id, password, task, in_progress, done, brainstorm = row
        if task:
            status = "Task"
            content = task
        elif in_progress:
            status = "In Progress"
            content = in_progress
        elif done:
            status = "Done"
            content = done
        elif brainstorm:
            status = "BrainStorm"
            content = brainstorm
        else:
            status = "Task"
            content = ""
        tasks.append({
            "id": task_id,
            "password": password,
            "status": status,
            "content": content
        })
    cur.close()
    conn.close()
    return tasks

def add_task(table_name, content, password, status):
    """Insert a new task into the table. Only the column matching the status gets the content."""
    conn = get_connection()
    cur = conn.cursor()
    task_id = str(uuid.uuid4())
    # Set content in the correct column, NULL in others.
    values = (
        task_id,
        password,
        content if status == "Task" else None,
        content if status == "In Progress" else None,
        content if status == "Done" else None,
        content if status == "BrainStorm" else None,
    )
    sql = f'''INSERT INTO {table_name} 
              (id, password, "Task", "In Progress", "Done", "BrainStorm")
              VALUES (%s, %s, %s, %s, %s, %s)'''
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    conn.close()

def delete_task(table_name, task_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table_name} WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()

def update_task_position(table_name, task_id, new_status):
    """Change the column where the card’s content is stored.
    This function finds the current column (non-null) and moves the content to new_status."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f'''SELECT "Task", "In Progress", "Done", "BrainStorm" 
                    FROM {table_name} WHERE id = %s''', (task_id,))
    row = cur.fetchone()
    content = None
    current_status = None
    if row:
        col_names = ["Task", "In Progress", "Done", "BrainStorm"]
        for idx, val in enumerate(row):
            if val is not None:
                content = val
                current_status = col_names[idx]
                break
    if content is None:
        cur.close()
        conn.close()
        return
    # Define mapping to properly quote columns (for names with spaces)
    columns = {"Task": "\"Task\"",
               "In Progress": "\"In Progress\"",
               "Done": "Done",
               "BrainStorm": "BrainStorm"}
    old_col = columns.get(current_status, "\"Task\"")
    new_col = columns.get(new_status, "\"Task\"")
    
    sql = f'''UPDATE {table_name} 
              SET {old_col} = NULL, {new_col} = %s 
              WHERE id = %s'''
    cur.execute(sql, (content, task_id))
    conn.commit()
    cur.close()
    conn.close()
