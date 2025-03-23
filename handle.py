import psycopg2
import streamlit as st

def get_connection():
    # Read connection string from Streamlit secrets
    conn_str = st.secrets["postgres"]["CONNECTION_STRING"]
    conn = psycopg2.connect(conn_str)
    return conn

def create_board(table, board_id, password):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            f"""INSERT INTO {table} 
            (id, password, Task, "In Progress", Done, BrainStorm)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (board_id, password, "", "", "", "")
        )
        conn.commit()
    except Exception as e:
        st.error(f"Error creating board: {e}")
    finally:
        cur.close()
        conn.close()

def get_board(table, board_id, password):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            f"""SELECT id, password, Task, "In Progress", Done, BrainStorm 
            FROM {table} 
            WHERE id = %s AND password = %s""",
            (board_id, password)
        )
        row = cur.fetchone()
        if row:
            board = {
                "id": row[0],
                "password": row[1],
                "Task": row[2].split("\n") if row[2] else [],
                "In Progress": row[3].split("\n") if row[3] else [],
                "Done": row[4].split("\n") if row[4] else [],
                "BrainStorm": row[5].split("\n") if row[5] else []
            }
            return board
        else:
            return None
    except Exception as e:
        st.error(f"Error retrieving board: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def update_board(table, board):
    # Join the list of tasks into newline-separated strings for storage
    conn = get_connection()
    cur = conn.cursor()
    try:
        task_str = "\n".join(board["Task"])
        in_progress_str = "\n".join(board["In Progress"])
        done_str = "\n".join(board["Done"])
        brainstorm_str = "\n".join(board["BrainStorm"])
        cur.execute(
            f"""UPDATE {table} 
            SET Task = %s, "In Progress" = %s, Done = %s, BrainStorm = %s 
            WHERE id = %s AND password = %s""",
            (task_str, in_progress_str, done_str, brainstorm_str, board["id"], board["password"])
        )
        conn.commit()
    except Exception as e:
        st.error(f"Error updating board: {e}")
    finally:
        cur.close()
        conn.close()

def add_task_to_board(table, board, column, task):
    if column in board:
        board[column].append(task)
        update_board(table, board)
    else:
        st.error("Invalid column.")

def move_task_in_board(table, board, from_column, to_column, task):
    if from_column in board and to_column in board:
        if task in board[from_column]:
            board[from_column].remove(task)
            board[to_column].append(task)
            update_board(table, board)
        else:
            st.error("Task not found in the selected column.")
    else:
        st.error("Invalid column.")

def delete_task_from_board(table, board, column, task):
    if column in board:
        if task in board[column]:
            board[column].remove(task)
            update_board(table, board)
        else:
            st.error("Task not found.")
    else:
        st.error("Invalid column.")
