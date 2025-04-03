import streamlit as st
from streamlit_sortables import sort_items
import psycopg2

@st.cache_resource
def get_connection():
    conn = psycopg2.connect(st.secrets["connections"]["neon"]["url"])
    conn.autocommit = True
    return conn

def init_db():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS boards (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                board_id INTEGER NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
                "column" TEXT NOT NULL,
                content TEXT NOT NULL,
                position INTEGER NOT NULL
            );
        """)

def get_boards():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM boards ORDER BY name;")
        rows = cur.fetchall()
        return [{"id": r[0], "name": r[1]} for r in rows]

def add_board(name):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO boards (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id;",
                (name,)
            )
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                cur.execute("SELECT id FROM boards WHERE name=%s;", (name,))
                row = cur.fetchone()
                return row[0] if row else None
    except Exception as e:
        st.error(f"Error adding board: {e}")
        return None

def get_tasks(board_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, \"column\", content, position FROM tasks WHERE board_id=%s ORDER BY position;",
            (board_id,)
        )
        rows = cur.fetchall()
        return [
            {"id": r[0], "column": r[1], "content": r[2], "position": r[3]}
            for r in rows
        ]

def add_card(board_id, column, content):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COALESCE(MAX(position), -1) FROM tasks WHERE board_id=%s AND \"column\"=%s;",
            (board_id, column)
        )
        max_pos = cur.fetchone()[0]
        new_pos = max_pos + 1
        cur.execute(
            "INSERT INTO tasks (board_id, \"column\", content, position) VALUES (%s, %s, %s, %s);",
            (board_id, column, content, new_pos)
        )

def delete_card(task_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id=%s;", (task_id,))

def move_card(task_id, new_column, new_position):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE tasks SET \"column\"=%s, position=%s WHERE id=%s;",
            (new_column, new_position, task_id)
        )
