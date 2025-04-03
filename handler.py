import psycopg2
import streamlit as st

def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(
        st.secrets["postgresql"]["url"],
        sslmode='require'
    )

def add_card(board_id, content, status):
    """添加新卡片"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (board_id, content, status) VALUES (%s, %s, %s)",
        (board_id, content, status)
    )
    conn.commit()
    cur.close()
    conn.close()

def move_card(card_id, new_status):
    """移动卡片到新状态"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tasks SET status = %s WHERE id = %s",
        (new_status, card_id)
    )
    conn.commit()
    cur.close()
    conn.close()

def delete_card(card_id):
    """删除卡片"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (card_id,))
    conn.commit()
    cur.close()
    conn.close()

def get_all_cards(board_id):
    """获取所有卡片"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, content, status FROM tasks WHERE board_id = %s",
        (board_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return [{"id": row[0], "content": row[1], "status": row[2]} for row in rows]
