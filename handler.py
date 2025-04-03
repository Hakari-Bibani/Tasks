import psycopg2
import pandas as pd
import streamlit as st
from psycopg2 import sql

class DatabaseHandler:
    def __init__(self):
        self.conn = None
    
    def get_connection(self):
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(st.secrets["db_connection"])
        return self.conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Create boards table if not exists
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS boards (
                        id SERIAL PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL
                    );
                """)
                
                # Create tasks table if not exists
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id TEXT PRIMARY KEY,
                        board_name TEXT NOT NULL,
                        task_column TEXT NOT NULL,
                        content TEXT NOT NULL,
                        position INTEGER
                    );
                """)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
    
    def get_all_boards(self):
        """Get all board names"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM boards ORDER BY name;")
                return [row[0] for row in cur.fetchall()]
        except Exception as e:
            st.error(f"Database error: {str(e)}")
            return []
    
    def create_board(self, board_name):
        """Create a new board"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO boards (name) VALUES (%s) ON CONFLICT DO NOTHING;",
                    (board_name,)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
    
    def get_board_data(self, board_name):
        """Get all tasks for a board as a dataframe"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT task_column, content 
                    FROM tasks 
                    WHERE board_name = %s
                    ORDER BY position;
                """, (board_name,))
                
                # Convert to dataframe with columns as separate columns
                data = cur.fetchall()
                if not data:
                    return pd.DataFrame(columns=["Task", "In Progress", "Done", "BrainStorm"])
                
                df = pd.DataFrame(data, columns=["column", "content"])
                pivoted = df.pivot(columns="column", values="content")
                return pivoted.reindex(columns=["Task", "In Progress", "Done", "BrainStorm"])
        except Exception as e:
            st.error(f"Database error: {str(e)}")
            return pd.DataFrame()
    
    def add_task(self, board_name, task_id, content, column):
        """Add a new task to a board"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Get current max position for this column
                cur.execute("""
                    SELECT COALESCE(MAX(position), 0) 
                    FROM tasks 
                    WHERE board_name = %s AND task_column = %s;
                """, (board_name, column))
                position = cur.fetchone()[0] + 1
                
                # Insert new task
                cur.execute("""
                    INSERT INTO tasks (id, board_name, task_column, content, position)
                    VALUES (%s, %s, %s, %s, %s);
                """, (task_id, board_name, column, content, position))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
    
    def update_column_tasks(self, board_name, column_name, tasks):
        """Update all tasks for a specific column"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Delete existing tasks for this column
                cur.execute("""
                    DELETE FROM tasks 
                    WHERE board_name = %s AND task_column = %s;
                """, (board_name, column_name))
                
                # Insert updated tasks with new positions
                for position, content in enumerate(tasks, 1):
                    cur.execute("""
                        INSERT INTO tasks (id, board_name, task_column, content, position)
                        VALUES (%s, %s, %s, %s, %s);
                    """, (str(uuid.uuid4()), board_name, column_name, content, position))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e

# Create single instance
db = DatabaseHandler()

# Helper functions for Streamlit
def init_db():
    db.init_db()

def get_all_boards():
    return db.get_all_boards()

def create_board(board_name):
    db.create_board(board_name)

def get_board_data(board_name):
    return db.get_board_data(board_name)

def add_task(board_name, task_id, content, column):
    db.add_task(board_name, task_id, content, column)

def update_column_tasks(board_name, column_name, tasks):
    db.update_column_tasks(board_name, column_name, tasks)
