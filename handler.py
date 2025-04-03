import os
import psycopg2

# Database connection parameters from Streamlit secrets
DB_CONN_STR = os.getenv("DB_CONNECTION")  # This will be set via Streamlit secrets

def get_board_data(table_name):
    """Retrieve all cards from the given board table, grouped by column."""
    conn = psycopg2.connect(DB_CONN_STR)
    cur = conn.cursor()
    # Fetch id and text of each card in each column (exclude password column)
    query = f'''
        SELECT id, "Task", "In Progress", "Done", "BrainStorm"
        FROM {table_name};
    '''
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Organize cards by column
    data = {"Task": [], "In Progress": [], "Done": [], "BrainStorm": []}
    for row in rows:
        card_id = row[0]
        for col_index, col_name in enumerate(data.keys(), start=1):
            text = row[col_index]
            if text not in (None, ""):
                data[col_name].append((card_id, text))
                break
    return data

def verify_password(table_name, password):
    """Check if the provided password matches the board's password."""
    conn = psycopg2.connect(DB_CONN_STR)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE password = %s;", (password,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count > 0

def add_card(table_name, password, column, text):
    """Insert a new task card into the specified column of the board."""
    conn = psycopg2.connect(DB_CONN_STR)
    cur = conn.cursor()
    # Insert new row with the given text in the appropriate column, and store the board password
    query = f'INSERT INTO {table_name} (password, "{column}") VALUES (%s, %s);'
    cur.execute(query, (password, text))
    conn.commit()
    cur.close()
    conn.close()

def update_card_column(table_name, card_id, old_column, new_column):
    """Move a card from old_column to new_column by updating the database."""
    conn = psycopg2.connect(DB_CONN_STR)
    cur = conn.cursor()
    # Set new_column to the old column's text, and clear the old column
    query = f'UPDATE {table_name} SET "{new_column}" = "{old_column}", "{old_column}" = NULL WHERE id = %s;'
    cur.execute(query, (card_id,))
    conn.commit()
    cur.close()
    conn.close()

def delete_card(table_name, card_id):
    """Delete a task card by its ID."""
    conn = psycopg2.connect(DB_CONN_STR)
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table_name} WHERE id = %s;", (card_id,))
    conn.commit()
    cur.close()
    conn.close()
