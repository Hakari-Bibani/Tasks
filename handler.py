import psycopg2
import pandas as pd
import streamlit as st
from psycopg2 import sql
import uuid

# Database connection
def get_connection():
    return psycopg2.connect(st.secrets["db_connection"])

def generate_id():
    return str(uuid.uuid4())

def get_all_boards():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'board_%'
                ORDER BY table_name;
            """)
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()

def create_board(board_name):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            table_name = f"board_{generate_id().replace('-', '_')}"
            cur.execute(sql.SQL("""
                CREATE TABLE {} (
                    id TEXT PRIMARY KEY,
                    "Task" TEXT,
                    "In Progress" TEXT,
                    "Done" TEXT,
                    "BrainStorm" TEXT
                );
            """).format(sql.Identifier(table_name)))
            
            # Store board mapping
            cur.execute("""
                INSERT INTO board_mapping (board_name, table_name) 
                VALUES (%s, %s);
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
            
            # Update the specific column
            cur.execute(sql.SQL("""
                INSERT INTO {} (id, "Task", "In Progress", "Done", "BrainStorm")
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    "{}" = %s;
            """).format(
                sql.Identifier(table_name),
                sql.Identifier(column)
            ), (
                task_id,
                "" if column != "Task" else content,
                "" if column != "In Progress" else content,
                "" if column != "Done" else content,
                "" if column != "BrainStorm" else content,
                content
            ))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_column_order(board_name, column_name, new_order):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name FROM board_mapping WHERE board_name = %s;
            """, (board_name,))
            table_name = cur.fetchone()[0]
            
            # Clear the column first
            cur.execute(sql.SQL("""
                UPDATE {} SET "{}" = '';
            """).format(
                sql.Identifier(table_name),
                sql.Identifier(column_name)
            )
            
            # Add items in new order
            for task_content in new_order:
                task_id = generate_id()
                add_task_to_board(board_name, task_id, task_content, column_name)
                
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Initialize database
def init_db():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS board_mapping (
                    board_name TEXT PRIMARY KEY,
                    table_name TEXT UNIQUE
                );
            """)
        conn.commit()
    finally:
        conn.close()

init_db()
