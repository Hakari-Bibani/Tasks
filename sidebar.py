import streamlit as st
from handlers import get_connection

def show_sidebar():
    with st.sidebar:
        st.title("Kanban Settings")
        
        # Board selection
        conn = get_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name LIKE 'table%'
                    """)
                    tables = [row[0] for row in cur.fetchall()]
                    selected_table = st.selectbox(
                        "Select Board",
                        tables,
                        index=0
                    )
                    st.session_state.current_board = selected_table
            except Exception as e:
                st.error(f"Error loading boards: {str(e)}")
            finally:
                conn.close()
        
        # New board creation
        new_board = st.text_input("Create New Board", placeholder="board_name")
        if st.button("Create") and new_board:
            create_board(new_board)
            st.rerun()

def create_board(board_name):
    conn = get_connection()
    if not conn:
        return
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("""
                CREATE TABLE IF NOT EXISTS {} (
                    id TEXT PRIMARY KEY,
                    Task TEXT,
                    "In Progress" TEXT,
                    Done TEXT,
                    "BrainStorm" TEXT
                )
            """).format(sql.Identifier(board_name)))
            conn.commit()
            st.success(f"Board {board_name} created!")
    except Exception as e:
        st.error(f"Create board failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()
