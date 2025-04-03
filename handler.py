import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseHandler:
    def __init__(self, connection_string):
        self.conn_string = connection_string
        
    def get_connection(self):
        return psycopg2.connect(self.conn_string)

    def get_cards(self, table_name):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(f'SELECT * FROM {table_name}')
                return cur.fetchall()

    def insert_card(self, table_name, data):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                columns = ', '.join(data.keys())
                values = ', '.join(['%s'] * len(data))
                query = f'INSERT INTO {table_name} ({columns}) VALUES ({values})'
                cur.execute(query, list(data.values()))
                conn.commit()

    def update_card(self, table_name, card_id, column, new_value):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Clear the value from all columns first
                update_query = f'''
                    UPDATE {table_name} 
                    SET "Task" = CASE WHEN 'Task' = %s THEN %s ELSE NULL END,
                        "In Progress" = CASE WHEN 'In Progress' = %s THEN %s ELSE NULL END,
                        "Done" = CASE WHEN 'Done' = %s THEN %s ELSE NULL END,
                        "BrainStorm" = CASE WHEN 'BrainStorm' = %s THEN %s ELSE NULL END
                    WHERE id = %s
                '''
                cur.execute(update_query, (column, new_value, column, new_value, column, new_value, column, new_value, card_id))
                conn.commit()

    def delete_card(self, table_name, card_id):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f'DELETE FROM {table_name} WHERE id = %s', (card_id,))
                conn.commit()
