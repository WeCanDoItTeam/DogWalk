import streamlit as st
from dbmanager import get_connection

# 사용자 인증 함수
def verify_user_credentials(user_id: str, user_passwd: str) -> bool:
    conn = get_connection() # DB 연결
    cursor = conn.cursor(dictionary=True) 
    # SQL 쿼리 동작 (사용자 아이디에 해당하는 해시된 비밀번호 조회) --> user_id가 %s에 대입
    cursor.execute("SELECT user_id FROM users WHERE user_id = %s AND user_passwd = %s", (user_id,user_passwd))
    result = cursor.fetchone() # {'user_id': 'user_id'} ==> 못 찾으면 None 반환
    # DB 연결 종료
    cursor.close()
    conn.close()
    
    return result is not None


def login_window():
    # 보더콜리 이미지와 LOGIN 글씨 표시 (이미지는 차후 수정 또는 배제 가능)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("assets/보더콜리.jpg", width=200)
        st.title("LOGIN")
    
    # 세션 상태가 초기화되지 않았으면 기본값 설정
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'dog_id' not in st.session_state: # Maria DB 접근을 위한 dog_id도 세션에 저장
        st.session_state.dog_id = None

    user_id = st.text_input(label="", placeholder="사용자 아이디")
    user_passwd = st.text_input(label="", placeholder="비밀번호", type="password")

    # 차후 클릭할 수 있게 기능 추가 예정
    st.write("<b>비밀번호를 잊으셨나요?</b>", unsafe_allow_html=True)

    if st.button("다음"):
        if not user_id or not user_passwd: # ID나 비밀번호가 비어있는 경우
            st.error("아이디와 비밀번호를 모두 입력해주세요.")
        if verify_user_credentials(user_id, user_passwd):
            st.session_state.user_id = user_id
            st.session_state.logged_in = True
            st.session_state.page = "menu"
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 잘못되었습니다.")  
    # 여백 추가        
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    
    # "계정을 만드세요!" 버튼 클릭시 register_user 화면으로
    col1, col2 = st.columns(2)
    with col1:
        st.write("등록하지 않으셨나요?")
    with col2: 
        if st.button("계정을 만드세요!"):
            st.session_state.page = 'register_user'