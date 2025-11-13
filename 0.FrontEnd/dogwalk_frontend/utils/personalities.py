import streamlit as st
import mysql.connector
from dbmanager import get_connection

def get_personality_traits():
    """등록된 모든 성격 특성을 가져옵니다."""
    conn = get_connection()
    if not conn: 
        st.error("데이터베이스 연결에 실패했습니다.")
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT personality_trait FROM personalities")
        return [row[0] for row in cursor.fetchall()]
    except mysql.connector.Error as e:
        st.error(f"성격 특성 조회 중 오류가 발생했습니다: {e}")
        return []
    finally:
        cursor.close()
        conn.close()