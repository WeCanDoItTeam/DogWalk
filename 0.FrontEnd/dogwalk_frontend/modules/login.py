import streamlit as st
from modules import register_dog, register_user
import pymysql

db_config = st.secrets["mariadb"]

# ✅ DB 연결 함수
def get_db_connection():
    return pymysql.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

# ✅ 사용자 인증 함수
def authenticate_user(user_id, user_passwd):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE user_id = %s AND user_passwd = %s"
            cursor.execute(sql, (user_id, user_passwd))
            result = cursor.fetchone()
            return result is not None
    finally:
        conn.close()

def render_login_page():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("assets/보더콜리.jpg", width=200)
        st.title("LOGIN")

    user_id = st.text_input(label="", placeholder="사용자 아이디")
    user_passwd = st.text_input(label="", placeholder="비밀번호")

    st.write("<b>비밀번호를 잊으셨나요?</b>", unsafe_allow_html=True)

    if st.button("다음"):
        if user_id in st.session_state["authenticated"] and 
        if user_id == "admin" and user_passwd == "1234": # 임의로 설정
            st.session_state["authenticated"] = True
            st.session_state["user"] = user_id
            st.success("Login successful!")
            
            # 페이지를 새로고침하여 app.py의 라우팅 로직이 
            # 메인 페이지를 렌더링하도록 합니다.
            st.rerun() 
        else:
            st.error("정보가 맞지 않습니다")

    # if st.button("계정을 만드세요!"):
    #     create_account.render_create_account_page()
        
render_login_page()