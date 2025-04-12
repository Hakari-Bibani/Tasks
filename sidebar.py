import streamlit as st
import psycopg2
import pandas as pd

CONNECTION_STRING = "postgresql://neondb_owner:npg_vJSrcVfZ7N6a@ep-snowy-bar-a5zv1qhw-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"

def get_connection():
    return psycopg2.connect(CONNECTION_STRING)

def get_boards():
    conn = get_connection()
    query = "SELECT * FROM boards ORDER BY created_at;"
    boards = pd.read_sql(query, conn)
    conn.close()
    return boards.to_dict(orient="records")

def create_board(board_id, board_name):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO boards (board_id, board_name) VALUES (%s, %s);", (board_id, board_name))
    conn.commit()
    conn.close()

def delete_board(board_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM boards WHERE board_id = %s;", (board_id,))
    conn.commit()
    conn.close()

def render_sidebar():
    st.sidebar.header("Board Management")
    boards = get_boards()
    
    board_names = [b["board_name"] for b in boards]
    current_board_name = st.sidebar.selectbox("Select Board", board_names)
    
    # Find the board record based on the selected name.
    current_board = next(b for b in boards if b["board_name"] == current_board_name)
    
    if st.sidebar.button("New Board"):
        new_name = st.sidebar.text_input("Enter new board name:")
        if new_name:
            import uuid
            new_board_id = str(uuid.uuid4())
            create_board(new_board_id, new_name)
            st.experimental_rerun()
    
    if st.sidebar.button("Delete Current Board"):
        delete_board(current_board["board_id"])
        st.experimental_rerun()
    
    return current_board
