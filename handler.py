import psycopg2
import pandas as pd
import streamlit as st
from psycopg2 import sql
from cryptography.fernet import Fernet
import hashlib
import os
import uuid

# Security Configuration
class SecurityManager:
    def __init__(self):
        self.key = self._get_encryption_key()
        self.cipher = Fernet(self.key)
    
    def _get_encryption_key(self):
        """Get encryption key from environment or generate a secure one"""
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key().decode()
            if st.secrets.get("encryption"):
                key = st.secrets["encryption"]["key"]
        return key.encode()
    
    def encrypt_data(self, data):
        """Encrypt sensitive data before storage"""
        if not data:
            return None
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data for display"""
        if not encrypted_data:
            return None
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def hash_password(self, password):
        """Secure password hashing"""
        salt = os.getenv('SALT', 'default-secure-salt').encode()
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        ).hex()

security = SecurityManager()

# Database Connection Manager
class DBManager:
    def __init__(self):
        self.conn_params = self._get_connection_params()
    
    def _get_connection_params(self):
        """Secure connection parameter handling"""
        if st.secrets.get("db_connection"):
            return st.secrets["db_connection"]
        raise ValueError("No database connection configured")
    
    def get_connection(self):
        """Get secure database connection"""
        return psycopg2.connect(**self.conn_params)
    
    def execute_query(self, query, params=None, return_df=False):
        """Secure query execution with automatic connection handling"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query, params)
                if return_df:
                    columns = [desc[0] for desc in cur.description]
                    data = cur.fetchall()
                    return pd.DataFrame(data, columns=columns)
                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                    conn.commit()
                    return cur.rowcount
                return cur.fetchall()
        except Exception as e:
            if conn:
                conn.rollback()
            st.error(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

db_manager = DBManager()

# Application Database Operations
def init_db():
    """Initialize secure database structure"""
    queries = [
        """CREATE TABLE IF NOT EXISTS board_mapping (
            board_name TEXT PRIMARY KEY,
            table_name TEXT UNIQUE
        );""",
        """CREATE TABLE IF NOT EXISTS auth (
            id SERIAL PRIMARY KEY,
            password_hash TEXT NOT NULL
        );""",
        """INSERT INTO auth (password_hash) 
           VALUES (%s) 
           ON CONFLICT DO NOTHING;""",
    ]
    
    # Set default password if none exists
    default_password = security.hash_password("admin123")
    
    for query in queries:
        if "%s" in query:
            db_manager.execute_query(query, (default_password,))
        else:
            db_manager.execute_query(query)

def verify_password(password):
    """Secure password verification"""
    hashed_input = security.hash_password(password)
    result = db_manager.execute_query(
        "SELECT password_hash FROM auth LIMIT 1;"
    )
    if result:
        return hashed_input == result[0][0]
    return False

def update_password(new_password):
    """Securely update password"""
    hashed_password = security.hash_password(new_password)
    db_manager.execute_query(
        "UPDATE auth SET password_hash = %s;",
        (hashed_password,)
    )

def generate_secure_id():
    """Generate cryptographically secure IDs"""
    return str(uuid.uuid4())

def get_all_boards():
    """Get all boards with secure query"""
    return db_manager.execute_query(
        """SELECT board_name FROM board_mapping ORDER BY board_name;""",
        return_df=False
    )

def create_board(board_name):
    """Create new board with secure table"""
    table_name = f"board_{generate_secure_id().replace('-', '_')}"
    
    db_manager.execute_query(
        sql.SQL("""
            CREATE TABLE {} (
                id TEXT PRIMARY KEY,
                Task TEXT,
                "In Progress" TEXT,
                Done TEXT,
                BrainStorm TEXT
            );
        """).format(sql.Identifier(table_name))
    )
    
    db_manager.execute_query(
        """INSERT INTO board_mapping (board_name, table_name) 
           VALUES (%s, %s);""",
        (board_name, table_name)
    )

def get_board_data(board_name):
    """Get encrypted board data"""
    table_name = db_manager.execute_query(
        "SELECT table_name FROM board_mapping WHERE board_name = %s;",
        (board_name,),
        return_df=False
    )[0][0]
    
    return db_manager.execute_query(
        sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)),
        return_df=True
    )

def add_task_to_board(board_name, task_id, content, column):
    """Securely add task with encrypted content"""
    table_name = db_manager.execute_query(
        "SELECT table_name FROM board_mapping WHERE board_name = %s;",
        (board_name,),
        return_df=False
    )[0][0]
    
    # Clear task from all columns first
    db_manager.execute_query(
        sql.SQL("""
            INSERT INTO {} (id, Task, "In Progress", Done, BrainStorm)
            VALUES (%s, '', '', '', '')
            ON CONFLICT (id) DO UPDATE SET
                Task = '',
                "In Progress" = '',
                Done = '',
                BrainStorm = '';
        """).format(sql.Identifier(table_name)),
        (task_id,)
    )
    
    # Update specific column with encrypted data
    column_map = {
        "Task": "Task",
        "In Progress": "In Progress",
        "Done": "Done",
        "BrainStorm": "BrainStorm"
    }
    
    db_manager.execute_query(
        sql.SQL("UPDATE {} SET {} = %s WHERE id = %s;").format(
            sql.Identifier(table_name),
            sql.Identifier(column_map[column])
        ),
        (content, task_id)
    )

def clear_board(board_name):
    """Securely clear board data"""
    table_name = db_manager.execute_query(
        "SELECT table_name FROM board_mapping WHERE board_name = %s;",
        (board_name,),
        return_df=False
    )[0][0]
    
    db_manager.execute_query(
        sql.SQL("TRUNCATE TABLE {}").format(sql.Identifier(table_name))
    )

# Initialize database securely
init_db()
