import streamlit as st
from dbmanager import get_connection
import bcrypt

def register_new_user(user_id: str, user_passwd: str) -> bool:
    try:
        conn = get_connection() # DB 연결
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if cursor.fetchone():
            st.error("이미 존재하는 아이디입니다.")
            cursor.close()
            conn.close()
            return False
        # gensalt(): 보안 위해 매번 다른 PW 해시값을 만들기 위한 랜덤 데이터
        hashed_passwd = bcrypt.hashpw(user_passwd.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (user_id, user_passwd) VALUES (%s, %s)",
                       (user_id, hashed_passwd.decode('utf-8')))
        conn.commit() # DB에 저장
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"회원가입 중 오류가 발생했습니다. {str(e)}")
        return False

def register_user_window():
    st.title("회원가입")
    
    # 세션 상태에서 임시 사용자 ID를 저장할 공간 확보
    # 강아지 정보까지 받고 user_id가 생성되게 구현
    if 'temp_user_id' not in st.session_state:
        st.session_state.temp_user_id = None

    new_user_id = st.text_input("아이디")
    new_user_passwd = st.text_input("비밀번호", type="password")
    confirm_passwd = st.text_input("비밀번호 확인", type="password")

    if st.button("다음", key="final_user_register"):
        if not new_user_id or not new_user_passwd:
            st.error("아이디와 비밀번호를 입력해주세요.")
        elif len(new_user_id) > 20 or len(new_user_passwd) > 20:
            st.error("아이디와 비밀번호는 20자 이내로 입력해야 합니다.")
        elif new_user_passwd != confirm_passwd:
            st.error("비밀번호가 일치하지 않습니다.")
        else:
            if register_new_user(new_user_id, new_user_passwd):
                # 사용자 등록 성공 후, 강아지 등록 창으로 넘어가기 위해 세션에 ID 저장
                st.session_state.temp_user_id = new_user_id
                st.session_state.page = 'register_dog' # 3. 성공 시 "강아지 정보등록" window로 전환
                st.rerun()
            
    if st.button("뒤로가기", key="back_to_login_from_register"):
        st.session_state.page = 'login'
        st.rerun()