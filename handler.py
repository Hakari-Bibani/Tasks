import streamlit as st
import psycopg2

def get_connection():
    """
    Establish and return a connection to the Neon PostgreSQL database.
    Uses the DATABASE_URL stored in Streamlit secrets.
    """
    # The DATABASE_URL should be set in your Streamlit secrets.
    connection_string = st.secrets["DATABASE_URL"]
    try:
        conn = psycopg2.connect(connection_string)
        return conn
    except Exception as e:
        st.error("Error connecting to the database:")
        st.error(e)
        st.stop()
