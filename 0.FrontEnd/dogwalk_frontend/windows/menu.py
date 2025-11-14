import streamlit as st

def menu_window():
    """메뉴 창 (추후 구현 예정)"""
    st.title("🐾 메인 메뉴")
    st.header(f"환영합니다, {st.session_state.user_id}님!")
    
    if st.session_state.dog_id:
        st.info(f"선택된 강아지 ID: **{st.session_state.dog_id}**")
        st.warning("여기에 메뉴 기능들을 구현하세요.")
    else:
        st.error("등록된 강아지 정보가 없습니다. 관리자에게 문의하세요.")
    
    # 로그아웃 기능
    if st.button("로그아웃", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.dog_id = None
        st.session_state.page = 'login'
        st.rerun()
    # 하단 네비게이션 바 (앱 스타일)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        home_button = st.button("🏠\n\n홈", key="nav_home", use_container_width=True)
    
    with col2:
        stats_button = st.button("📊\n\n통계", key="nav_stats", use_container_width=True)
    
    with col3:
        settings_button = st.button("⚙️\n\n설정", key="nav_settings", use_container_width=True)
    
    # 버튼 클릭 처리
    if home_button:
        st.session_state.page = 'menu'
        st.rerun()
    
    if stats_button:
        st.info("통계 페이지로 이동 (구현 예정)")
        # st.session_state.page = 'stats'
        # st.rerun()
    
    if settings_button:
        st.info("설정 페이지로 이동 (구현 예정)")
        # st.session_state.page = 'settings'
        # st.rerun()