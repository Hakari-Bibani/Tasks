import psycopg2
import streamlit as st

# Retrieve your connection string from secrets (set this in your Streamlit sharing or local config)
CONNECTION_STRING = st.secrets["connection_string"]

def get_connection():
    return psycopg2.connect(CONNECTION_STRING)

def get_tables():
    # For simplicity, we return a static list.
    # Alternatively, you could query PostgreSQL's catalog (information_schema.tables) filtering on your board naming convention.
    return ["table1", "table2", "table3", "table4", "table5", "table6"]

def add_table(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    # Make sure table_name is sanitized to avoid SQL injection.
    query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id TEXT PRIMARY KEY,
        "Task" TEXT,
        "In Progress" TEXT,
        "Done" TEXT,
        "BrainStorm" TEXT
    );
    """
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

def get_cards(table_name):
    """
    Returns a dictionary where keys are column names (statuses) and values are lists of card dicts.
    For this simple design, assume that each row holds one card in one of the status columns.
    (You might need a more normalized design in a full implementation.)
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = f"SELECT id, \"Task\", \"In Progress\", Done, BrainStorm FROM {table_name};"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Initialize a dictionary for statuses
    cards = {"Task": [], "In Progress": [], "Done": [], "Brain Storm": []}
    for row in rows:
        card_id = row[0]
        # For each status column, if there is content, treat it as a card
        statuses = ["Task", "In Progress", "Done", "BrainStorm"]
        for i, status in enumerate(statuses, start=1):
            if row[i] is not None and row[i].strip() != "":
                # Use "Brain Storm" as key in our dictionary if needed
                key = "Brain Storm" if status == "BrainStorm" else status
                cards[key].append({"id": card_id, "content": row[i]})
    return cards

def add_card(table_name, status, card_id, content):
    """
    Inserts a new card into the specified column of the board.
    In this simple schema, we insert a row with the content only in the specified column.
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Determine the column name in the table.
    # Note: if status is "Brain Storm" in UI, map it to "BrainStorm" in DB.
    column = "BrainStorm" if status == "Brain Storm" else status
    query = f"INSERT INTO {table_name} (id, \"{column}\") VALUES (%s, %s);"
    cursor.execute(query, (card_id, content))
    conn.commit()
    cursor.close()
    conn.close()

def update_card_status(table_name, card_id, new_status, new_content):
    """
    Updates the card's content in the target status column.
    In a full implementation, you’d likely clear the old status and update the new one.
    """
    conn = get_connection()
    cursor = conn.cursor()
    column = "BrainStorm" if new_status == "Brain Storm" else new_status
    query = f"UPDATE {table_name} SET \"{column}\" = %s WHERE id = %s;"
    cursor.execute(query, (new_content, card_id))
    conn.commit()
    cursor.close()
    conn.close()
