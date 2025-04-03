import streamlit as st
import psycopg2

# Singleton connection to the Postgres database
@st.experimental_singleton
def get_connection():
    # Connect using the URL from Streamlit secrets
    conn = psycopg2.connect(st.secrets["connections"]["neon"]["url"])
    conn.autocommit = True  # enable auto-commit for convenience
    return conn

def init_db():
    """Create boards and tasks tables if they do not exist."""
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
                column TEXT NOT NULL,
                content TEXT NOT NULL,
                position INTEGER NOT NULL
            );
        """)

def get_boards():
    """Return a list of all boards as dicts: {"id": ..., "name": ...}."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM boards ORDER BY name;")
        rows = cur.fetchall()
        return [{"id": r[0], "name": r[1]} for r in rows]

def add_board(name):
    """Add a new board with the given name. Returns the board id, or None if not created."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO boards (name) VALUES (%s) "
                "ON CONFLICT (name) DO NOTHING RETURNING id;",
                (name,)
            )
            result = cur.fetchone()
            if result:
                # New board created
                return result[0]
            else:
                # Board name already exists, fetch its id
                cur.execute("SELECT id FROM boards WHERE name=%s;", (name,))
                row = cur.fetchone()
                return row[0] if row else None
    except Exception as e:
        st.error(f"Error adding board: {e}")
        return None

def get_tasks(board_id):
    """Fetch all tasks for the given board, as a list of dicts."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, column, content, position FROM tasks "
            "WHERE board_id=%s ORDER BY position;",
            (board_id,)
        )
        rows = cur.fetchall()
        return [
            {"id": r[0], "column": r[1], "content": r[2], "position": r[3]}
            for r in rows
        ]

# Alias for clarity – fetching board data (tasks) 
fetch_board_data = get_tasks

def add_card(board_id, column, content):
    """Insert a new task into the given board/column with the next position index."""
    conn = get_connection()
    with conn.cursor() as cur:
        # Find the highest position in this column to determine the new card's position
        cur.execute(
            "SELECT COALESCE(MAX(position), -1) FROM tasks WHERE board_id=%s AND column=%s;",
            (board_id, column)
        )
        max_pos = cur.fetchone()[0]
        new_pos = max_pos + 1
        cur.execute(
            "INSERT INTO tasks (board_id, column, content, position) VALUES (%s, %s, %s, %s);",
            (board_id, column, content, new_pos)
        )

def delete_card(task_id):
    """Delete the task with the given id."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id=%s;", (task_id,))

def move_card(task_id, new_column, new_position):
    """Update task's column and position (used for drag-and-drop reordering)."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE tasks SET column=%s, position=%s WHERE id=%s;",
            (new_column, new_position, task_id)
        )
