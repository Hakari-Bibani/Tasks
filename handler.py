import psycopg2
import pandas as pd
import streamlit as st
from psycopg2 import sql

# Database connection
def get_connection():
    return psycopg2.connect(st.secrets["db_connection"])

def get_all_boards():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'table%'
                ORDER BY table_name;
            """)
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()

def create_board(board_name):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            table_name = f"table{len(get_all_boards()) + 1}"
            cur.execute(sql.SQL("""
                CREATE TABLE {} (
                    id TEXT PRIMARY KEY,
                    Task TEXT,
                    "In Progress" TEXT,
                    Done TEXT,
                    BrainStorm TEXT
                );
            """).format(sql.Identifier(table_name)))
            
            # Store board mapping (you might want to use a separate table for this in production)
            cur.execute("""
                INSERT INTO board_mapping (board_name, table_name) 
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """, (board_name, table_name))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_board_data(board_name):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name FROM board_mapping WHERE board_name = %s;
            """, (board_name,))
            table_name = cur.fetchone()[0]
            
            cur.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
            columns = [desc[0] for desc in cur.description]
            data = cur.fetchall()
            
            return pd.DataFrame(data, columns=columns)
    finally:
        conn.close()

def add_task_to_board(board_name, task_id, content, column):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name FROM board_mapping WHERE board_name = %s;
            """, (board_name,))
            table_name = cur.fetchone()[0]
            
            # Clear the task from all columns first
            cur.execute(sql.SQL("""
                INSERT INTO {} (id, Task, "In Progress", Done, BrainStorm)
                VALUES (%s, '', '', '', '')
                ON CONFLICT (id) DO UPDATE SET
                    Task = '',
                    "In Progress" = '',
                    Done = '',
                    BrainStorm = '';
            """).format(sql.Identifier(table_name)), (task_id,))
            
            # Update the specific column
            if column == "Task":
                update_col = "Task"
            elif column == "In Progress":
                update_col = "In Progress"
            else:
                update_col = column
                
            cur.execute(sql.SQL("""
                UPDATE {} SET {} = %s WHERE id = %s;
            """).format(
                sql.Identifier(table_name),
                sql.Identifier(update_col)
            ), (content, task_id))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def clear_board(board_name):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name FROM board_mapping WHERE board_name = %s;
            """, (board_name,))
            table_name = cur.fetchone()[0]
            cur.execute(sql.SQL("TRUNCATE TABLE {}").format(sql.Identifier(table_name)))
        conn.commit()
    finally:
        conn.close()

# Initialize database (run once)
def init_db():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS board_mapping (
                    board_name TEXT PRIMARY
