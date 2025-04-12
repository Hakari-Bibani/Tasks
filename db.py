import streamlit as st
import psycopg2
import uuid

# Database connection
def get_connection():
    return psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        database=st.secrets["postgres"]["database"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"],
        sslmode="require"
    )

# Get all items from the database
def get_all_items():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, Task, \"In Progress\", Done, BrainStorm FROM table1")
    items = cur.fetchall()
    cur.close()
    conn.close()
    
    # Organize items by category
    tasks = []
    in_progress = []
    done = []
    brainstorm = []
    
    for item in items:
        item_id = item[0]
        if item[1]:  # Task
            tasks.append({"id": item_id, "text": item[1]})
        if item[2]:  # In Progress
            in_progress.append({"id": item_id, "text": item[2]})
        if item[3]:  # Done
            done.append({"id": item_id, "text": item[3]})
        if item[4]:  # BrainStorm
            brainstorm.append({"id": item_id, "text": item[4]})
    
    return {
        "Task": tasks,
        "In Progress": in_progress,
        "Done": done,
        "BrainStorm": brainstorm
    }

# Add a new item
def add_item(column, text):
    conn = get_connection()
    cur = conn.cursor()
    item_id = str(uuid.uuid4())
    
    # Create a dictionary with all columns set to None
    item_data = {
        "Task": None,
        "In Progress": None,
        "Done": None,
        "BrainStorm": None
    }
    
    # Set the specified column to the text
    item_data[column] = text
    
    # Insert into database
    cur.execute(
        "INSERT INTO table1 (id, Task, \"In Progress\", Done, BrainStorm) VALUES (%s, %s, %s, %s, %s)",
        (item_id, item_data["Task"], item_data["In Progress"], item_data["Done"], item_data["BrainStorm"])
    )
    
    conn.commit()
    cur.close()
    conn.close()
    return item_id

# Update an item when moved to a different column
def move_item(item_id, from_column, to_column, text):
    conn = get_connection()
    cur = conn.cursor()
    
    # First, get the current item
    cur.execute(f"SELECT id, Task, \"In Progress\", Done, BrainStorm FROM table1 WHERE id = %s", (item_id,))
    item = cur.fetchone()
    
    if item:
        # Update the item: clear the old column and set the new column
        update_query = f"UPDATE table1 SET \"{from_column}\" = NULL, \"{to_column}\" = %s WHERE id = %s"
        cur.execute(update_query, (text, item_id))
        conn.commit()
    
    cur.close()
    conn.close()

# Delete an item
def delete_item(item_id):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM table1 WHERE id = %s", (item_id,))
    conn.commit()
    
    cur.close()
    conn.close()
