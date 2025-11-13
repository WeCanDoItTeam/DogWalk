import streamlit as st

def render_main_page():

    st.title("🐾 메인 메뉴")
    st.write("환영합니다!")

    # 여기에 기존 main.py의 모든 대시보드/앱 로직을 추가합니다.
    st.dataframe({
        'col1': [1, 2, 3],
        'col2': [10, 20, 30]
    })

# render_main_page()