import psycopg2
import pandas as pd

# Create a global connection (consider using a connection pool for production)
CONNECTION_STRING = "postgresql://neondb_owner:npg_vJSrcVfZ7N6a@ep-snowy-bar-a5zv1qhw-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"

def get_connection():
    conn = psycopg2.connect(CONNECTION_STRING)
    return conn

def get_tasks_for_board(board_id):
    conn = get_connection()
    query = "SELECT * FROM table1 WHERE board_id = %s ORDER BY created_at;"
    tasks = pd.read_sql(query, conn, params=(board_id,))
    conn.close()
    return tasks.to_dict(orient="records")

def update_task_status(task_id, new_status):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE table1 SET status = %s WHERE task_id = %s;", (new_status, task_id))
    conn.commit()
    conn.close()

def add_task(board_id, task_text, status="Task"):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO table1 (board_id, task_text, status) VALUES (%s, %s, %s);", (board_id, task_text, status))
    conn.commit()
    conn.close()

def edit_task(task_id, new_text):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE table1 SET task_text = %s WHERE task_id = %s;", (new_text, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM table1 WHERE task_id = %s;", (task_id,))
    conn.commit()
    conn.close()
