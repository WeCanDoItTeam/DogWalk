import streamlit as st
import time

st.set_page_config(page_title="Survey App", layout="centered")

# --- Initialize session state ---
if "page" not in st.session_state:
    st.session_state.page = "loading"

# --- Simulate loading screen ---
if st.session_state.page == "loading":
    st.markdown(
        """
        <style>
        .loader {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 22px;
            color: #0066ff;
            font-family: 'Arial', sans-serif;
        }
        </style>
        <div class="loader">
            <strong>Loading...</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Simulate loading process
    time.sleep(2)
    st.session_state.page = "survey"
    st.rerun()

# --- Survey Screen ---
elif st.session_state.page == "survey":
    st.title("설문조사")

    name = st.text_input("Your Name")
    age = st.number_input("Age", min_value=10, max_value=100, step=1)
    gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])
    interests = st.multiselect(
        "What are you interested in?", ["Technology", "Art", "Science", "Sports", "Travel"]
    )
    satisfaction = st.radio(
        "How satisfied are you with our website?",
        ["Very satisfied", "Satisfied", "Neutral", "Dissatisfied"],
    )

    st.markdown(
        """
        <style>
        div.stButton > button:first-child {
            background-color: #007BFF;
            color: white;
            width: 100%;
            padding: 0.75em;
            border-radius: 6px;
            font-size: 18px;
        }
        div.stButton > button:hover {
            background-color: #0056b3;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Submit"):
        st.session_state.page = "login"
        st.rerun()

# --- Login Screen ---
elif st.session_state.page == "login":
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    st.markdown(
        """
        <style>
        div.stButton > button:first-child {
            background-color: #007BFF;
            color: white;
            width: 100%;
            padding: 0.75em;
            border-radius: 6px;
            font-size: 18px;
        }
        div.stButton > button:hover {
            background-color: #0056b3;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Login"):
        st.success("Login successful!")