"""
handle.py

This module handles all database connectivity and queries.
It provides:
- get_connection(): returns a psycopg2 database connection
- get_tasks(table_name): returns a list of dicts containing rows from the given table
- add_task(table_name, column, text): inserts a new row with 'text' in the specified column
- update_task_column(table_name, item_id, from_column, to_column): moves text from one column to another
"""

import os
import psycopg2
import uuid

# 1. Optionally read from an environment variable named DATABASE_URL
# 2. Fallback to your Neon connection string if no environment variable is set
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_vJSrcVfZ7N6a@ep-snowy-bar-a5zv1qhw-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

def get_connection():
    """
    Returns a psycopg2 connection to the database.
    """
    return psycopg2.connect(DATABASE_URL)

def get_tasks(table_name: str):
    """
    Returns all rows from the specified table as a list of dicts with keys:
    ['id', 'Task', 'In Progress', 'Done', 'BrainStorm'].
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = f'''
        SELECT id, "Task", "In Progress", "Done", "BrainStorm"
        FROM {table_name}
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "Task": row[1],
            "In Progress": row[2],
            "Done": row[3],
            "BrainStorm": row[4]
        })
    return results

def add_task(table_name: str, column: str, text: str):
    """
    Inserts a new row into table_name with the given text in the specified column.
    column must be one of 'Task', 'In Progress', 'Done', or 'BrainStorm'.
    """
    if column not in ["Task", "In Progress", "Done", "BrainStorm"]:
        raise ValueError("Invalid column name provided.")

    conn = get_connection()
    cursor = conn.cursor()

    new_id = str(uuid.uuid4())
    query = f'''
        INSERT INTO {table_name} (id, "{column}")
        VALUES (%s, %s)
    '''
    cursor.execute(query, (new_id, text))
    conn.commit()
    cursor.close()
    conn.close()

def update_task_column(table_name: str, item_id: str, from_column: str, to_column: str):
    """
    Moves the text from 'from_column' to 'to_column' for a given 'item_id'.
    This sets 'from_column' to NULL and 'to_column' to the old text.
    """
    if from_column not in ["Task", "In Progress", "Done", "BrainStorm"]:
        raise ValueError("Invalid from_column name provided.")
    if to_column not in ["Task", "In Progress", "Done", "BrainStorm"]:
        raise ValueError("Invalid to_column name provided.")

    conn = get_connection()
    cursor = conn.cursor()

    # Fetch the existing text from 'from_column'
    select_query = f'''
        SELECT "{from_column}"
        FROM {table_name}
        WHERE id = %s
    '''
    cursor.execute(select_query, (item_id,))
    result = cursor.fetchone()

    if not result:
        # No row found
        cursor.close()
        conn.close()
        return

    text_to_move = result[0]
    if not text_to_move:
        # There's no text in the from_column to move
        cursor.close()
        conn.close()
        return

    # Update the row: set from_column to NULL, set to_column to text_to_move
    update_query = f'''
        UPDATE {table_name}
        SET "{from_column}" = NULL,
            "{to_column}" = %s
        WHERE id = %s
    '''
    cursor.execute(update_query, (text_to_move, item_id))
    conn.commit()

    cursor.close()
    conn.close()
