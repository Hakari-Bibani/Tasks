import os
import psycopg2
from psycopg2 import sql
import streamlit as st

@st.cache_resource
def get_connection():
    try:
        return psycopg2.connect(os.environ['NEONDB_URI'])
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def get_tasks(table_name, column_name):
    conn = get_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cur:
            query = sql.SQL("""
                SELECT id, {} AS content 
                FROM {}
                WHERE {} IS NOT NULL AND {} <> ''
            """).format(
                sql.Identifier(column_name),
                sql.Identifier(table_name),
                sql.Identifier(column_name),
                sql.Identifier(column_name)
            )
            cur.execute(query)
            return [{'id': row[0], 'content': row[1]} for row in cur.fetchall()]
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return []
    finally:
        conn.close()

def add_task(table_name, column_name, content):
    conn = get_connection()
    if not conn:
        return
    
    try:
        with conn.cursor() as cur:
            task_id = f"task_{hash(content + column_name)}"
            query = sql.SQL("""
                INSERT INTO {} (id, {})
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET {} = EXCLUDED.{}
            """).format(
                sql.Identifier(table_name),
                sql.Identifier(column_name),
                sql.Identifier(column_name),
                sql.Identifier(column_name)
            )
            cur.execute(query, (task_id, content))
            conn.commit()
    except Exception as e:
        st.error(f"Add task failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def move_task(table_name, task_id, old_column, new_column):
    conn = get_connection()
    if not conn:
        return
    
    try:
        with conn.cursor() as cur:
            query = sql.SQL("""
                UPDATE {}
                SET {} = NULL, {} = (
                    SELECT {} FROM {} WHERE id = %s
                )
                WHERE id = %s
            """).format(
                sql.Identifier(table_name),
                sql.Identifier(old_column),
                sql.Identifier(new_column),
                sql.Identifier(old_column),
                sql.Identifier(table_name)
            )
            cur.execute(query, (task_id, task_id))
            conn.commit()
    except Exception as e:
        st.error(f"Move task failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()
