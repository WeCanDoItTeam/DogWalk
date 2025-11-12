import streamlit as st
from modules import login, main

# 페이지 구성을 넓게 사용
st.set_page_config(layout="wide")

# 처음 접속 시 딕셔너리에 "authenticated"와 "user" key를 만듦
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None

# --- 라우팅 로직 ---
if st.session_state["authenticated"] == False:
    login.render_login_page()
else:
    # 인증되었다면 사이드바에 로그아웃 버튼과 네비게이션 생성
    st.sidebar.markdown(f"Welcome, **{st.session_state['user']}**!")
    
    if st.sidebar.button("로그아웃"):
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.rerun()  # 로그아웃 후 즉시 새로고침하여 로그인 페이지로 이동

    # 메인 앱 페이지 함수 호출
    main.render_main_page()