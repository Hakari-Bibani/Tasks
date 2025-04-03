import os
import json
from sqlalchemy import create_engine, text
import streamlit as st  # Used here for accessing st.secrets if available

# Retrieve your PostgreSQL connection string.
# For online deployment on Streamlit Sharing, store this value in your secrets.
# Example secrets.toml structure:
# [database]
# DB_CONNECTION_STRING = "postgresql://neondb_owner:npg_vJSrcVfZ7N6a@ep-snowy-bar-a5zv1qhw-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
conn_str = os.environ.get("DB_CONNECTION_STRING")
if not conn_str and "database" in st.secrets and "DB_CONNECTION_STRING" in st.secrets["database"]:
    conn_str = st.secrets["database"]["DB_CONNECTION_STRING"]

engine = create_engine(conn_str)

def get_board(table_name, board_id):
    """Retrieve a board from the given table. Returns a dict or None."""
    query = text(f"SELECT * FROM {table_name} WHERE id = :id")
    with engine.connect() as conn:
        result = conn.execute(query, {"id": board_id}).fetchone()
        if result:
            board = dict(result)
            # Convert JSON strings to lists; if empty, default to an empty list.
            for col in ["Task", "In Progress", "Done", "BrainStorm"]:
                board[col] = json.loads(board[col]) if board[col] else []
            return board
        else:
            return None

def create_board(table_name, board_id, password):
    """Create a new board with empty columns and the given password."""
    default_data = {
        "id": board_id,
        "password": password,
        "Task": json.dumps([]),
        "In Progress": json.dumps([]),
        "Done": json.dumps([]),
        "BrainStorm": json.dumps([])
    }
    query = text(
        f"""INSERT INTO {table_name} 
        (id, password, Task, "In Progress", Done, BrainStorm)
        VALUES (:id, :password, :Task, :InProgress, :Done, :BrainStorm)"""
    )
    with engine.connect() as conn:
        conn.execute(query, {
            "id": board_id,
            "password": password,
            "Task": default_data["Task"],
            "InProgress": default_data["In Progress"],
            "Done": default_data["Done"],
            "BrainStorm": default_data["BrainStorm"]
        })
        conn.commit()

def update_board(table_name, board_id, board_data):
    """Update the board row with new card data."""
    data = {
        "Task": json.dumps(board_data["Task"]),
        "InProgress": json.dumps(board_data["In Progress"]),
        "Done": json.dumps(board_data["Done"]),
        "BrainStorm": json.dumps(board_data["BrainStorm"]),
        "id": board_id
    }
    query = text(
        f"""UPDATE {table_name} SET 
        Task = :Task, "In Progress" = :InProgress, 
        Done = :Done, BrainStorm = :BrainStorm 
        WHERE id = :id"""
    )
    with engine.connect() as conn:
        conn.execute(query, data)
        conn.commit()

def add_card(table_name, board_id, column, card_text):
    board = get_board(table_name, board_id)
    board[column].append(card_text)
    update_board(table_name, board_id, board)

def delete_card(table_name, board_id, column, card_index):
    board = get_board(table_name, board_id)
    if 0 <= card_index < len(board[column]):
        board[column].pop(card_index)
        update_board(table_name, board_id, board)

def move_card(table_name, board_id, from_column, to_column, card_index):
    board = get_board(table_name, board_id)
    if 0 <= card_index < len(board[from_column]):
        card = board[from_column].pop(card_index)
        board[to_column].append(card)
        update_board(table_name, board_id, board)
