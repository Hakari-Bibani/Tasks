import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd

class DatabaseHandler:
    def __init__(self, db_url):
        """
        Initialize the database handler with connection details.
        
        Args:
            db_url (str): PostgreSQL connection URL
        """
        self.db_url = db_url
        self.test_connection()
    
    def test_connection(self):
        """Test the database connection."""
        try:
            conn = psycopg2.connect(self.db_url)
            conn.close()
        except Exception as e:
            raise Exception(f"Database connection failed: {e}")
    
    def get_connection(self):
        """Create and return a database connection."""
        return psycopg2.connect(self.db_url)
    
    def get_available_tables(self):
        """Get list of available tables in the database."""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                tables = [row[0] for row in cur.fetchall()]
        
        return tables
    
    def check_table_exists(self, table_name):
        """Check if a table exists in the database."""
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (table_name,))
                exists = cur.fetchone()[0]
        
        return exists
    
    def get_all_tasks(self, table_name):
        """Get all tasks from the specified table."""
        query = f"""
        SELECT id, "Task", "In Progress", "Done", "BrainStorm" 
        FROM "{table_name}";
        """
        
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                tasks = cur.fetchall()
        
        return tasks
    
    def add_task(self, table_name, task_id, task_content):
        """Add a new task to the specified table."""
        query = f"""
        INSERT INTO "{table_name}" (id, "Task", "In Progress", "Done", "BrainStorm")
        VALUES (%s, %s, NULL, NULL, NULL);
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (task_id, task_content))
            conn.commit()
    
    def move_task(self, table_name, task_id, target_column):
        """Move a task to a different column in the specified table."""
        # First, get the current task content
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(f'SELECT * FROM "{table_name}" WHERE id = %s', (task_id,))
                task = cur.fetchone()
        
        if task:
            # Determine which column currently has content
            content = None
            current_column = None
            
            for col in ["Task", "In Progress", "Done", "BrainStorm"]:
                if task[col]:
                    content = task[col]
                    current_column = col
                    break
            
            if content and current_column:
                # Update the task, moving it to the target column
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        # Reset all columns
                        reset_query = f"""
                        UPDATE "{table_name}" 
                        SET "Task" = NULL, "In Progress" = NULL, "Done" = NULL, "BrainStorm" = NULL
                        WHERE id = %s
                        """
                        cur.execute(reset_query, (task_id,))
                        
                        # Set the target column
                        update_query = f"""
                        UPDATE "{table_name}" 
                        SET "{target_column}" = %s
                        WHERE id = %s
                        """
                        cur.execute(update_query, (content, task_id))
                    conn.commit()
    
    def delete_task(self, table_name, task_id):
        """Delete a task from the specified table."""
        query = f"""
        DELETE FROM "{table_name}" WHERE id = %s;
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (task_id,))
            conn.commit()
