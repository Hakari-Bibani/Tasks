import streamlit as st
import psycopg2
import os

class DatabaseHandler:
    def __init__(self):
        """Initialize database connection using Streamlit secrets or environment variables"""
        self.conn = self._get_connection()
    
    def _get_connection(self):
        """Establish database connection using secrets or environment variables"""
        # Try to get connection string from Streamlit secrets
        if hasattr(st, "secrets") and "postgres" in st.secrets:
            # Using Streamlit secrets (preferred for deployment)
            conn_string = st.secrets["postgres"]["url"]
        else:
            # Fallback to environment variable or hardcoded for development
            conn_string = os.environ.get(
                "DATABASE_URL", 
                "postgresql://neondb_owner:npg_vJSrcVfZ7N6a@ep-snowy-bar-a5zv1qhw-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
            )
        
        try:
            conn = psycopg2.connect(conn_string)
            return conn
        except Exception as e:
            st.error(f"Database connection error: {e}")
            return None
    
    def board_exists(self, table_name):
        """Check if a board exists in the table"""
        if not self.conn:
            return False
        
        try:
            cur = self.conn.cursor()
            # Check if any rows exist in the table
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            cur.close()
            return count > 0
        except Exception as e:
            st.error(f"Error checking board: {e}")
            return False
    
    def create_board(self, table_name):
        """Create a new board"""
        if not self.conn:
            return False
        
        try:
            cur = self.conn.cursor()
            # Delete any existing rows (clean slate)
            cur.execute(f"DELETE FROM {table_name}")
            
            # Create initial board settings row
            cur.execute(
                f"INSERT INTO {table_name} (id, \"Task\", \"In Progress\", \"Done\", \"BrainStorm\") "
                f"VALUES (%s, %s, %s, %s, %s)",
                ("settings", None, None, None, None)
            )
            
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            st.error(f"Board creation error: {e}")
            return False
    
    def get_all_tasks(self, table_name):
        """Get all tasks from the board"""
        if not self.conn:
            return []
        
        try:
            cur = self.conn.cursor()
            cur.execute(
                f"SELECT id, \"Task\", \"In Progress\", \"Done\", \"BrainStorm\" FROM {table_name} WHERE id != 'settings'"
            )
            tasks = []
            for row in cur.fetchall():
                tasks.append({
                    "id": row[0],
                    "Task": row[1],
                    "In Progress": row[2],
                    "Done": row[3],
                    "BrainStorm": row[4]
                })
            cur.close()
            return tasks
        except Exception as e:
            st.error(f"Error fetching tasks: {e}")
            return []
    
    def add_task(self, table_name, task_id, task=None, in_progress=None, done=None, brainstorm=None):
        """Add a new task to the board"""
        if not self.conn:
            return False
        
        try:
            cur = self.conn.cursor()
            cur.execute(
                f"INSERT INTO {table_name} (id, \"Task\", \"In Progress\", \"Done\", \"BrainStorm\") "
                f"VALUES (%s, %s, %s, %s, %s)",
                (task_id, task, in_progress, done, brainstorm)
            )
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            st.error(f"Error adding task: {e}")
            return False
    
    def move_task(self, table_name, task_id, from_column, to_column):
        """Move a task from one column to another"""
        if not self.conn:
            return False
        
        try:
            cur = self.conn.cursor()
            # Get the task content from the source column
            cur.execute(f"SELECT \"{from_column}\" FROM {table_name} WHERE id = %s", (task_id,))
            task_content = cur.fetchone()[0]
            # Update the task: set the source column to NULL and the destination column to the content
            cur.execute(
                f"UPDATE {table_name} SET \"{from_column}\" = NULL, \"{to_column}\" = %s WHERE id = %s",
                (task_content, task_id)
            )
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            st.error(f"Error moving task: {e}")
            return False
    
    def delete_task(self, table_name, task_id):
        """Delete a task from the board"""
        if not self.conn:
            return False
        
        try:
            cur = self.conn.cursor()
            cur.execute(f"DELETE FROM {table_name} WHERE id = %s", (task_id,))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            st.error(f"Error deleting task: {e}")
            return False
