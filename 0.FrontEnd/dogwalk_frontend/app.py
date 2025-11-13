import streamlit as st
from windows.login import login_window
from windows.register_user import register_user_window
from windows.register_dog import register_dog_window
from windows.menu import menu_window

# 페이지 구성을 넓게 사용 (1번만 명시)
st.set_page_config(layout="wide")

# 세션 상태에 'page' 키가 없으면 기본값으로 'login' 페이지로 설정 (앱 최초 접속 시 로그인 화면으로)
# st.session_state는 Streamlit의 세션 상태 관리 딕셔너리!
if 'page' not in st.session_state:
    st.session_state.page = 'login'
    
# 윈도우(화면) 라우팅 구조
def main():
    """세션 상태에 따라 적절한 화면을 렌더링합니다."""
    # 요청에 따라 페이지 분할
    if st.session_state.page == 'login':
        login_window()
    elif st.session_state.page == 'register_user':
        register_user_window()
    elif st.session_state.page == 'register_dog':
        register_dog_window()
    elif st.session_state.page == 'menu':
        menu_window()
    else:
        # 오류 처리 또는 기본 페이지로 리다이렉트
        st.session_state.page = 'login'
        st.rerun()

if __name__ == "__main__":
    main()