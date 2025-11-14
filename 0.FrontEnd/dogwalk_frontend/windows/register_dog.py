import streamlit as st
from dbmanager import get_connection
from datetime import date
from utils.dog_details import register_dog_and_details
from utils.vaccines import get_vaccine_names
from utils.personalities import get_personality_traits

def register_dog_window():
    """강아지 정보, 예방 접종, 성격 등록 창을 표시합니다."""
    st.title("🐕 강아지 정보 등록")
    user_id = st.session_state.get('temp_user_id')
    if not user_id:
        st.error('사용자 정보를 찾을 수 없습니다.')
        st.session_state.page = 'register_user'
        st.rerun()
        return
    
    # 데이터 로드
    all_vaccines = get_vaccine_names()
    all_personalities = get_personality_traits()

    st.subheader("강아지 기본 정보")
    
    # 4. dogs 테이블 정보 입력
    dog_name = st.text_input("강아지 이름 (name)", key="dog_name", max_chars=20)
    dog_birthdate = st.date_input("생일 (birthdate)", value=date.today(), max_value=date.today(), key="dog_birthdate")
    dog_gender = st.selectbox("성별 (gender)", ['Male', 'Female', 'Unknown'], key="dog_gender")
    dog_breed = st.text_input("견종 (breed)", key="dog_breed", max_chars=50)
    dog_weight = st.number_input("몸무게 (kg) (weight)", min_value=0.1, max_value=100.0, step=0.1, key="dog_weight")
    
    # is_neutered는 TINYINT(1)이므로 True/False로 입력받는 것이 적절
    neutered_options = {True: '예 (중성화)', False: '아니오 (미중성화)'}
    is_neutered_label = st.radio("중성화 여부", options=list(neutered_options.values()), index=1, key="dog_neutered_radio")
    is_neutered_value = [k for k, v in neutered_options.items() if v == is_neutered_label][0]


    st.subheader("예방 접종 정보")
    # injection_date 입력
    vaccination_records = {}
    for vaccine in all_vaccines:
        col_v, col_d = st.columns([1, 1])
        with col_v:
            is_checked = st.checkbox(vaccine, key=f"vac_check_{vaccine}")
        with col_d:
            if is_checked:
                injection_date = st.date_input(
                    "접종일", 
                    value=date.today(), 
                    max_value=date.today(), 
                    key=f"vac_date_{vaccine}",
                    label_visibility="collapsed"
                )
                vaccination_records[vaccine] = injection_date
    

    st.subheader("성격 특성")
    # personalities table 정보 입력
    selected_personalities = st.multiselect(
        "강아지의 성격을 선택해 주세요",
        options=all_personalities,
        key="dog_personalities_select"
    )

    if st.button("등록 완료 및 메뉴로 이동", key="finalize_dog_register"):
        if not dog_name or not dog_breed or dog_weight <= 0:
            st.error("강아지 기본 정보를 모두 올바르게 입력해주세요.")
            return
        
        dog_data = {
            'name': dog_name,
            'birthdate': dog_birthdate,
            'gender': dog_gender,
            'breed': dog_breed,
            'weight': dog_weight,
            'is_neutered': is_neutered_value
        }

        # 실제로 접종일이 입력된 백신만 필터링
        active_vaccines = {name: date for name, date in vaccination_records.items()}

        # DB에 저장
        dog_id = register_dog_and_details(user_id, dog_data, active_vaccines, selected_personalities)

        if dog_id:
            # 5. 성공 시 세션 상태 업데이트 및 메뉴로 전환
            st.session_state.logged_in = True
            st.session_state.user_id = user_id # 신규 등록의 경우 temp_user_id를 user_id로 확정
            st.session_state.dog_id = dog_id
            st.session_state.temp_user_id = None # 임시 ID 초기화
            st.session_state.page = 'menu'
            st.success("강아지 정보 등록이 완료되었습니다!")
            st.rerun()
        else:
            st.error("정보 등록 중 오류가 발생했습니다. 다시 시도해주세요.")
    if st.button("뒤로가기", key='back_to_register_user'):
        st.session_state.page = 'register_user'
        st.rerun()