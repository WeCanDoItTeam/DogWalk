import streamlit as st
import mysql.connector
from dbmanager import get_connection

def get_vaccine_names():
    """등록된 모든 백신 이름을 가져옵니다."""
    conn = get_connection()
    if not conn: 
        st.error("데이터베이스 연결에 실패했습니다.")
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT vaccine_name FROM vaccines")
        return [row[0] for row in cursor.fetchall()]
    except mysql.connector.Error as e:
        st.error(f"백신 이름 조회 중 오류가 발생했습니다: {e}")
        return []
    finally:
        cursor.close()
        conn.close()