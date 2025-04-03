import psycopg2
import pandas as pd
import streamlit as st
from psycopg2 import sql

def get_connection():
    return psycopg2.connect(st.secrets["db_connection"])

def init_db():
    """Initialize database tables"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Create board mapping table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS board_mapping (
                    board_name TEXT PRIMARY KEY,
                    table_name TEXT UNIQUE NOT NULL
                );
            """)
        conn.commit()
    except Exception as e:
        conn.rollback()
        st.error(f"Database initialization error: {str(e)}")
    finally:
        conn.close()

def get_all_boards():
    """Get all board names"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT board_name FROM board_mapping ORDER BY board_name;")
            return [row[0] for row in cur.fetchall()]
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return []
    finally:
        conn.close()

def create_board(board_name):
    """Create a new board with its own table"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Create a unique table name
            table_name = f"board_{board_name.lower().replace(' ', '_')}"
            
            # Create the board table
            cur.execute(sql.SQL("""
                CREATE TABLE {} (
                    id TEXT PRIMARY KEY,
                    "Task" TEXT,
                    "In Progress" TEXT,
                    "Done" TEXT,
                    "BrainStorm" TEXT
                );
            """).format(sql.Identifier(table_name)))
            
            # Add to board mapping
            cur.execute("""
                INSERT INTO board_mapping (board_name, table_name)
                VALUES (%s, %s);
            """, (board_name, table_name))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        st.error(f"Error creating board: {str(e)}")
    finally:
        conn.close()

def get_board_data(board_name):
    """Get all tasks for a board"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Get the table name for this board
            cur.execute("""
                SELECT table_name FROM board_mapping WHERE board_name = %s;
            """, (board_name,))
            table_name = cur.fetchone()[0]
            
            # Get all tasks from the board's table
            cur.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
            columns = [desc[0] for desc in cur.description]
            data = cur.fetchall()
            
            return pd.DataFrame(data, columns=columns)
    except Exception as e:
        st.error(f"Error getting board data: {str(e)}")
        return pd.DataFrame()
    finally:
        conn.close()

def add_task_to_board(board_name, task_id, content, column):
    """Add a task to a specific column in a board"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Get the table name for this board
            cur.execute("""
                SELECT table_name FROM board_mapping WHERE board_name = %s;
            """, (board_name,))
            table_name = cur.fetchone()[0]
            
            # Clear the task from all columns first
            cur.execute(sql.SQL("""
                INSERT INTO {} (id, "Task", "In Progress", "Done", "BrainStorm")
                VALUES (%s, '', '', '', '')
                ON CONFLICT (id) DO UPDATE SET
                    "Task" = '',
                    "In Progress" = '',
                    "Done" = '',
                    "BrainStorm" = '';
            """).format(sql.Identifier(table_name)), (task_id,))
            
            # Update the specific column
            cur.execute(sql.SQL("""
                UPDATE {} SET "{}" = %s WHERE id = %s;
            """).format(
                sql.Identifier(table_name),
                sql.Identifier(column)
            ), (content, task_id))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding task: {str(e)}")
    finally:
        conn.close()

def clear_board(board_name):
    """Clear all tasks from a board"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Get the table name for this board
            cur.execute("""
                SELECT table_name FROM board_mapping WHERE board_name = %s;
            """, (board_name,))
            table_name = cur.fetchone()[0]
            
            # Clear the table
            cur.execute(sql.SQL("TRUNCATE TABLE {}").format(sql.Identifier(table_name)))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        st.error(f"Error clearing board: {str(e)}")
    finally:
        conn.close()
