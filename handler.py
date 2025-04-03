import streamlit as st
import psycopg2
import uuid

# Retrieve the connection string from Streamlit's secrets.
DB_CONN_STR = st.secrets["DB_CONNECTION"]

def get_board_data(table_name):
    """
    Retrieve all cards from the given board table, grouped by column.
    Each card is assumed to exist in one of the text columns.
    """
    conn = psycopg2.connect(DB_CONN_STR)
    cur = conn.cursor()
    query = f'''
        SELECT id, "Task", "In Progress", "Done", "BrainStorm"
        FROM {table_name};
    '''
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    data = {"Task": [], "In Progress": [], "Done": [], "BrainStorm": []}
    for row in rows:
        card_id = row[0]
        # Check each column in order; the first non-empty column is the current location.
        for idx, col_name in enumerate(data.keys(), start=1):
            text = row[idx]
            if text not in (None, ""):
                data[col_name].append((card_id, text))
                break
    return data

def verify_password(table_name, password):
    """
    Check if the provided password matches any entry in the board table.
    """
    conn = psycopg2.connect(DB_CONN_STR)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE password = %s;", (password,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count > 0

def add_card(table_name, password, column, text):
    """
    Insert a new task card into the specified column of the board.
    A unique UUID is generated for each card.
    """
    card_id = str(uuid.uuid4())
    conn = psycopg2.connect(DB_CONN_STR)
    cur = conn.cursor()
    query = f'INSERT INTO {table_name} (id, password, "{column}") VALUES (%s, %s, %s);'
    cur.execute(query, (card_id, password, text))
    conn.commit()
    cur.close()
    conn.close()

def update_card_column(table_name, card_id, old_column, new_column, text):
    """
    Move a card from old_column to new_column by updating the row.
    The card's text remains the same.
    """
    conn = psycopg2.connect(DB_CONN_STR)
    cur = conn.cursor()
    query = f'''
        UPDATE {table_name}
        SET "{new_column}" = %s, "{old_column}" = NULL
        WHERE id = %s;
    '''
    cur.execute(query, (text, card_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_card(table_name, card_id):
    """
    Delete a task card by its ID.
    """
    conn = psycopg2.connect(DB_CONN_STR)
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table_name} WHERE id = %s;", (card_id,))
    conn.commit()
    cur.close()
    conn.close()
