import os
import json
import streamlit as st
import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json

# Initialize the database connection
@st.cache_resource
def init_connection():
    """Initialize and cache the database connection using the DATABASE_URL secret."""
    # Get the connection string from Streamlit secrets (or environment variable as fallback)
    if "DATABASE_URL" in st.secrets:
        conn_str = st.secrets["DATABASE_URL"]
    else:
        conn_str = os.environ.get("DATABASE_URL", None)
    if conn_str is None:
        raise Exception("Database connection string not found. Set DATABASE_URL in Streamlit secrets or environment.")
    # Ensure sslmode=require for Neon, if not present in the connection string
    # (Neon requires SSL; connection strings from Neon usually have sslmode=require by default)
    if "sslmode" not in conn_str:
        conn = psycopg2.connect(conn_str, sslmode='require')
    else:
        conn = psycopg2.connect(conn_str)
    return conn

def get_board_data(table_name: str):
    """Fetch the tasks data for the given board (table). Returns four lists: tasks, in_progress, done, brainstorm."""
    # Only allow specific table names for safety
    if table_name not in [f"table{i}" for i in range(1, 7)]:
        raise ValueError("Invalid table name.")
    conn = init_connection()
    cur = conn.cursor()
    # Select the JSON lists from the table; cast to text for safe JSON parsing in Python
    query = sql.SQL("SELECT tasks::text, in_progress::text, done::text, brainstorm::text FROM {} WHERE id=%s;").format(sql.Identifier(table_name))
    cur.execute(query, (1,))
    row = cur.fetchone()
    if row is None:
        # If no row exists (fresh board), insert an initial empty row
        insert_query = sql.SQL("INSERT INTO {} (tasks, in_progress, done, brainstorm) VALUES (%s, %s, %s, %s);").format(sql.Identifier(table_name))
        cur.execute(insert_query, (Json([]), Json([]), Json([]), Json([])))
        conn.commit()
        # Return empty lists as the initial data
        return [], [], [], []
    # Parse JSON text into Python lists
    tasks_list = json.loads(row[0]) if row[0] else []
    in_progress_list = json.loads(row[1]) if row[1] else []
    done_list = json.loads(row[2]) if row[2] else []
    brainstorm_list = json.loads(row[3]) if row[3] else []
    return tasks_list, in_progress_list, done_list, brainstorm_list

def save_board_data(table_name: str, tasks_list, in_progress_list, done_list, brainstorm_list):
    """Save the given lists of tasks back into the specified board (table)."""
    # Ensure table name is valid
    if table_name not in [f"table{i}" for i in range(1, 7)]:
        raise ValueError("Invalid table name.")
    conn = init_connection()
    cur = conn.cursor()
    # Update the table with new JSON data
    query = sql.SQL("UPDATE {} SET tasks=%s, in_progress=%s, done=%s, brainstorm=%s WHERE id=%s;").format(sql.Identifier(table_name))
    cur.execute(query, (
        Json(tasks_list),
        Json(in_progress_list),
        Json(done_list),
        Json(brainstorm_list),
        1
    ))
    conn.commit()
    # (Optionally, could return success status or rowcount)
