import psycopg2
import streamlit as st
from typing import Dict, List

class DatabaseHandler:
    def __init__(self):
        # Get database credentials from Streamlit secrets
        self.db_credentials = {
            "dbname": st.secrets.db_credentials.dbname,
            "user": st.secrets.db_credentials.user,
            "password": st.secrets.db_credentials.password,
            "host": st.secrets.db_credentials.host,
            "sslmode": "require"
        }
    
    def connect(self):
        """Establish database connection"""
        try:
            conn = psycopg2.connect(**self.db_credentials)
            return conn
        except Exception as e:
            st.error(f"Database connection error: {str(e)}")
            return None
    
    def get_tasks(self, table_name: str) -> Dict[str, List[Dict]]:
        """Get all tasks for a board"""
        conn = self.connect()
        tasks = {
            'Tasks': [],
            'In Progress': [],
            'Done': [],
            'BrainStorm': []
        }
        
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    for row in rows:
                        if row[2]:  # "In Progress" column
                            tasks['In Progress'].append({'id': row[0], 'task': row[1]})
                        elif row[3]:  # "Done" column
                            tasks['Done'].append({'id': row[0], 'task': row[1]})
                        elif row[4]:  # "BrainStorm" column
                            tasks['BrainStorm'].append({'id': row[0], 'task': row[1]})
                        else:
                            tasks['Tasks'].append({'id': row[0], 'task': row[1]})
            finally:
                conn.close()
        return tasks
    
    def add_task(self, table_name: str, task: str):
        """Add a new task to a board"""
        conn = self.connect()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        INSERT INTO {table_name} (id, task)
                        VALUES (uuid_generate_v4(), %s)
                    """, (task,))
                    conn.commit()
            finally:
                conn.close()
    
    def delete_task(self, table_name: str, task_id: str):
        """Delete a task from a board"""
        conn = self.connect()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        DELETE FROM {table_name}
                        WHERE id = %s
                    """, (task_id,))
                    conn.commit()
            finally:
                conn.close()
