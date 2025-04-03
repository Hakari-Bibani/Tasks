import os
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from datetime import datetime

def get_db_connection():
    return psycopg2.connect(
        os.getenv('DATABASE_URL'),
        cursor_factory=RealDictCursor
    )

def add_card(table_name, column, content):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        card_id = str(uuid.uuid4())
        # Create a dict with all columns set to None initially
        columns = {'Task': None, 'In Progress': None, 'Done': None, 'BrainStorm': None}
        # Set the content for the specified column
        columns[column] = content
        
        query = f"""
        INSERT INTO {table_name} (id, "Task", "In Progress", "Done", "BrainStorm")
        VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query, (card_id, columns['Task'], columns['In Progress'], 
                          columns['Done'], columns['BrainStorm']))
        conn.commit()
    except Exception as e:
        print(f"Error adding card: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_cards(table_name, column):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = f'SELECT id, "{column}" FROM {table_name} WHERE "{column}" IS NOT NULL'
        cur.execute(query)
        return cur.fetchall()
    except Exception as e:
        print(f"Error getting cards: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def delete_card(table_name, card_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = f"DELETE FROM {table_name} WHERE id = %s"
        cur.execute(query, (card_id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting card: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
