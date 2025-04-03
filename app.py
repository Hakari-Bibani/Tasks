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
