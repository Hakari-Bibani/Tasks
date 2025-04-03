import psycopg2
from psycopg2.extras import DictCursor

# Database connection
def get_db_connection():
    return psycopg2.connect(
        "postgresql://neondb_owner:npg_vJSrcVfZ7N6a@ep-snowy-bar-a5zv1qhw-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
    )

# Create a new board (table)
def create_board(board_name):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {board_name} (
                    id SERIAL PRIMARY KEY,
                    column_name TEXT NOT NULL,
                    content TEXT NOT NULL
                )
                """
            )
            conn.commit()
    finally:
        conn.close()

# Get all boards (tables)
def list_boards():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()

# Get data for a specific board
def get_board_data(board_name):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(f"SELECT * FROM {board_name}")
            rows = cur.fetchall()
            data = {"Tasks": {}, "In Progress": {}, "Done": {}, "BrainStorm": {}}
            for row in rows:
                data[row["column_name"]][row["id"]] = row["content"]
            return data
    finally:
        conn.close()

# Add a new card
def add_card(board_name, column_name, content):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {board_name} (column_name, content) VALUES (%s, %s)",
                (column_name, content),
            )
            conn.commit()
    finally:
        conn.close()

# Delete a card
def delete_card(board_name, card_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {board_name} WHERE id = %s", (card_id,))
            conn.commit()
    finally:
        conn.close()

# Move a card between columns
def move_card(board_name, card_id, new_column):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE {board_name} SET column_name = %s WHERE id = %s",
                (new_column, card_id),
            )
            conn.commit()
    finally:
        conn.close()
