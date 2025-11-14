import streamlit as st
import mysql.connector
from dbmanager import get_connection

def register_dog_and_details(user_id, dog_data, vaccines, personalities):
    """강아지 정보, 예방 접종, 성격 정보를 일괄 등록합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    dog_id = None
    
    try:
        # 1. dogs 테이블 삽입
        cursor.execute(
            """INSERT INTO dogs (user_id, name, birthdate, gender, breed, weight, is_neutered) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (user_id, dog_data['name'], dog_data['birthdate'], dog_data['gender'], dog_data['breed'], dog_data['weight'], dog_data['is_neutered'])
        )
        
        dog_id = cursor.lastrowid # INSERT 성공 시: 1,2,3 // INSERT 실패 시: 0 또는 None
        
        if dog_id:
            # 2. vaccination_records 테이블 삽입
            for vaccine_name, injection_date in vaccines.items():
                cursor.execute(
                    "SELECT code_id FROM comm_code WHERE code_cd = 'vaccines' AND code_nm = %s", (vaccine_name,)
                )
                result = cursor.fetchone()
                if result:
                    vaccine_id = result[0]
                    cursor.execute(
                        """INSERT INTO vaccination_records (dog_id, vaccine_id, injection_date) VALUES (%s, %s, %s)""",
                        (dog_id, vaccine_id, injection_date)
                    )

            # 3. dog_personalities 테이블 삽입
            for personality_trait in personalities:
                cursor.execute(
                    "SELECT code_id FROM comm_code WHERE code_cd = 'personalities' AND code_nm = %s", (personality_trait,)
                )
                result = cursor.fetchone()
                if result:
                    personality_id = result[0]
                    cursor.execute(
                        """INSERT INTO dog_personalities (dog_id, personality_id) VALUES (%s, %s)""",
                        (dog_id, personality_id)
                    )

        conn.commit()
        return dog_id
    
    except mysql.connector.Error as e:
        st.error(f"데이터베이스 오류: {e}")
        conn.rollback() # 작업 취소
        return None
    except Exception as e:
        st.error(f"예상치 못한 오류: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()