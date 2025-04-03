import psycopg2
import json

# Global variable to hold the connection string
CONN_STR = None

def init_db(conn_str):
    """Initializes the database connection string."""
    global CONN_STR
    CONN_STR = conn_str

def get_connection():
    if not CONN_STR:
        raise Exception("Database not initialized. Call init_db(conn_str) first.")
    return psycopg2.connect(CONN_STR)

def get_board(table_name, board_id):
    """Retrieve a board (row) from the given table."""
    conn = get_connection()
    cur = conn.cursor()
    query = f"""
        SELECT id, password, "Task", "In Progress", Done, BrainStorm 
        FROM {table_name} 
        WHERE id = %s
    """
    cur.execute(query, (board_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {
            "id": row[0],
            "password": row[1],
            "Task": json.loads(row[2]) if row[2] else [],
            "In Progress": json.loads(row[3]) if row[3] else [],
            "Done": json.loads(row[4]) if row[4] else [],
            "BrainStorm": json.loads(row[5]) if row[5] else [],
        }
    else:
        return None

def create_board(table_name, board_id, password):
    """Creates a new board with empty lists for each column."""
    empty_list = json.dumps([])
    conn = get_connection()
    cur = conn.cursor()
    query = f"""
        INSERT INTO {table_name} (id, password, "Task", "In Progress", Done, BrainStorm)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur.execute(query, (board_id, password, empty_list, empty_list, empty_list, empty_list))
    conn.commit()
    cur.close()
    conn.close()

def update_board(table_name, board_id, board_data):
    """
    Updates the board columns with the new board_data.
    board_data should be a dict with keys: "Task", "In Progress", "Done", "BrainStorm".
    """
    conn = get_connection()
    cur = conn.cursor()
    query = f"""
        UPDATE {table_name}
        SET "Task" = %s,
            "In Progress" = %s,
            Done = %s,
            BrainStorm = %s
        WHERE id = %s
    """
    cur.execute(
        query,
        (
            json.dumps(board_data.get("Task", [])),
            json.dumps(board_data.get("In Progress", [])),
            json.dumps(board_data.get("Done", [])),
            json.dumps(board_data.get("BrainStorm", [])),
            board_id,
        ),
    )
    conn.commit()
    cur.close()
    conn.close()
