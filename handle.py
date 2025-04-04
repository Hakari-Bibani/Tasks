import os
import psycopg2
from psycopg2 import sql
import streamlit as st

@st.cache_resource
def get_connection():
    return psycopg2.connect(os.environ['NEONDB_URI'])

def get_tasks(board, column):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("SELECT id, {} as content FROM {}")
                .format(sql.Identifier(column), sql.Identifier(board))
            )
            return [{'id': row[0], 'content': row[1]} for row in cur.fetchall()]

def handle_task_update(board, task_id, column, content=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if 'new_task' in task_id:
                cur.execute(
                    sql.SQL("INSERT INTO {} (id, {}) VALUES (%s, %s)")
                    .format(sql.Identifier(board), sql.Identifier(column)),
                    (task_id, content)
                )
            else:
                cur.execute(
                    sql.SQL("UPDATE {} SET {} = %s WHERE id = %s")
                    .format(sql.Identifier(board), sql.Identifier(column)),
                    (content or column, task_id)
                )
            conn.commit()

def create_new_board(board_name):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("CREATE TABLE IF NOT EXISTS {} (id TEXT PRIMARY KEY, Task TEXT, \"In Progress\" TEXT, Done TEXT, BrainStorm TEXT)")
                .format(sql.Identifier(board_name))
            )
            conn.commit()
