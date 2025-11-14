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
    # 반환 예시: [(1, '1', '2024-01-15', 'vaccines', '01', '종합백신'), (1, '1', '2024-01-15', 'vaccines', '01', '종합백신')]
    try:
        cursor.execute("""SELECT code_id, code_nm FROM comm_code
                       WHERE code_cd='vaccines'
                       ORDER BY code_id""")
        return [{'id':row[0], 'name':row[1]} for row in cursor.fetchall()]
    except mysql.connector.Error as e:
        st.error(f"백신 이름 조회 중 오류가 발생했습니다: {e}")
        return []
    finally:
        cursor.close()
        conn.close()