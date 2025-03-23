import psycopg2
from datetime import datetime
import pandas as pd

class DatabaseHandler:
    def __init__(self, connection_string):
        self.conn_string = connection_string

    def get_connection(self):
        return psycopg2.connect(self.conn_string)

    def create_task(self, table_number, task_id, password, content, status):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        INSERT INTO table{table_number} (id, password, Task, "In Progress", Done, BrainStorm)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (task_id, password, 
                         content if status == "Task" else None,
                         content if status == "In Progress" else None,
                         content if status == "Done" else None,
                         content if status == "BrainStorm" else None)
                    )
            return True
        except Exception as e:
            print(f"Error creating task: {e}")
            return False

    def get_tasks(self, table_number):
        try:
            with self.get_connection() as conn:
                query = f"""
                SELECT id, password, Task, "In Progress", Done, BrainStorm 
                FROM table{table_number}
                """
                return pd.read_sql(query, conn)
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return pd.DataFrame()

    def verify_password(self, table_number, task_id, password):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT password FROM table{table_number}
                        WHERE id = %s
                        """,
                        (task_id,)
                    )
                    stored_password = cur.fetchone()
                    return stored_password and stored_password[0] == password
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False

    def update_task_status(self, table_number, task_id, content, new_status):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # First, set all status columns to NULL
                    cur.execute(
                        f"""
                        UPDATE table{table_number}
                        SET Task = NULL, "In Progress" = NULL, Done = NULL, BrainStorm = NULL
                        WHERE id = %s
                        """,
                        (task_id,)
                    )
                    
                    # Then, update the appropriate status column
                    status_column = new_status if new_status != "In Progress" else '"In Progress"'
                    cur.execute(
                        f"""
                        UPDATE table{table_number}
                        SET {status_column} = %s
                        WHERE id = %s
                        """,
                        (content, task_id)
                    )
            return True
        except Exception as e:
            print(f"Error updating task status: {e}")
            return False

    def delete_task(self, table_number, task_id):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        DELETE FROM table{table_number}
                        WHERE id = %s
                        """,
                        (task_id,)
                    )
            return True
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
