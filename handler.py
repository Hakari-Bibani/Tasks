import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseHandler:
    def __init__(self, connection_string):
        self.conn_string = connection_string

    def get_connection(self):
        return psycopg2.connect(self.conn_string)

    def get_cards_for_column(self, table_name, column):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Use the exact column name from the database
                cur.execute(f'SELECT * FROM {table_name} WHERE {column} IS NOT NULL')
                return cur.fetchall()

    def get_cards(self, table_name):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(f'SELECT * FROM {table_name}')
                return cur.fetchall()

    def insert_card(self, table_name, data):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['%s'] * len(data))
                query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
                cur.execute(query, list(data.values()))
                conn.commit()

    def update_card(self, table_name, card_id, column, new_value):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Clear all columns first and update the specific column
                update_query = f'''
                    UPDATE {table_name} 
                    SET task = CASE WHEN %s = 'task' THEN %s ELSE NULL END,
                        "in progress" = CASE WHEN %s = 'in progress' THEN %s ELSE NULL END,
                        done = CASE WHEN %s = 'done' THEN %s ELSE NULL END,
                        brainstorm = CASE WHEN %s = 'brainstorm' THEN %s ELSE NULL END
                    WHERE id = %s
                '''
                cur.execute(update_query, (column, new_value, column, new_value, column, new_value, column, new_value, card_id))
                conn.commit()

    def delete_card(self, table_name, card_id):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f'DELETE FROM {table_name} WHERE id = %s', (card_id,))
                conn.commit()
