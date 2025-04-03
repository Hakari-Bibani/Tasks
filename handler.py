import psycopg2
import streamlit as st

class DatabaseHandler:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=st.secrets["db_host"],
            database=st.secrets["db_name"],
            user=st.secrets["db_user"],
            password=st.secrets["db_password"],
            sslmode=st.secrets["sslmode"]
        )
        self.create_initial_tables()

    def create_initial_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS boards (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            )
        """)
        self.conn.commit()
        cursor.close()

    def create_board(self, board_name):
        cursor = self.conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS "{board_name}" (
                id TEXT PRIMARY KEY,
                column_name TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        cursor.execute("INSERT INTO boards (name) VALUES (%s)", (board_name,))
        self.conn.commit()
        cursor.close()

    def get_all_boards(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM boards")
        boards = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return boards

    def add_card(self, board_name, column_name, content):
        import uuid
        card_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        cursor.execute(f"""
            INSERT INTO "{board_name}" (id, column_name, content)
            VALUES (%s, %s, %s)
        """, (card_id, column_name, content))
        self.conn.commit()
        cursor.close()

    def get_cards(self, board_name, column_name):
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT id, content FROM "{board_name}"
            WHERE column_name = %s
        """, (column_name,))
        cards = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()
        return cards

    def move_card(self, board_name, card_id, new_column):
        cursor = self.conn.cursor()
        cursor.execute(f"""
            UPDATE "{board_name}"
            SET column_name = %s
            WHERE id = %s
        """, (new_column, card_id))
        self.conn.commit()
        cursor.close()

    def delete_card(self, board_name, card_id):
        cursor = self.conn.cursor()
        cursor.execute(f"""
            DELETE FROM "{board_name}"
            WHERE id = %s
        """, (card_id,))
        self.conn.commit()
        cursor.close()
