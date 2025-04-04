import psycopg2
import streamlit as st

# Retrieve your connection string from Streamlit Cloud secrets
CONNECTION_STRING = st.secrets["connection_string"]

def get_connection():
    return psycopg2.connect(CONNECTION_STRING)

def get_tables():
    # Return a static list of board names (table names)
    return ["table1", "table2", "table3", "table4", "table5", "table6"]

def add_table(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    # Create a table with proper column names:
    # - Unquoted names become lower-case (e.g., task, done, brainstorm)
    # - "In Progress" is quoted to preserve the space and case.
    query = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id TEXT PRIMARY KEY,
        task TEXT,
        "In Progress" TEXT,
        done TEXT,
        brainstorm TEXT
    );
    '''
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

def get_cards(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    # Use lower-case for unquoted columns and quote "In Progress" as created
    query = f'SELECT id, task, "In Progress", done, brainstorm FROM {table_name};'
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Prepare dictionary with keys matching the UI labels
    cards = {"Task": [], "In Progress": [], "Done": [], "Brain Storm": []}
    for row in rows:
        card_id = row[0]
        # row[1] is task, row[2] is "In Progress", row[3] is done, row[4] is brainstorm
        if row[1] and row[1].strip():
            cards["Task"].append({"id": card_id, "content": row[1]})
        if row[2] and row[2].strip():
            cards["In Progress"].append({"id": card_id, "content": row[2]})
        if row[3] and row[3].strip():
            cards["Done"].append({"id": card_id, "content": row[3]})
        if row[4] and row[4].strip():
            cards["Brain Storm"].append({"id": card_id, "content": row[4]})
    return cards

def add_card(table_name, status, card_id, content):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Map UI labels to the actual database column names
    column_map = {
        "Task": "task",
        "In Progress": "In Progress",  # This column name must be quoted in queries
        "Done": "done",
        "Brain Storm": "brainstorm"
    }
    column = column_map.get(status, status)
    
    # For "In Progress", include quotes around the column name
    if column == "In Progress":
        query = f'INSERT INTO {table_name} (id, "{column}") VALUES (%s, %s);'
    else:
        query = f'INSERT INTO {table_name} (id, {column}) VALUES (%s, %s);'
    
    cursor.execute(query, (card_id, content))
    conn.commit()
    cursor.close()
    conn.close()
