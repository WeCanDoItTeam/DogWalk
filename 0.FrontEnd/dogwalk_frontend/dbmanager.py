import streamlit as st
import mysql.connector

def get_connection():
    """Connect to MariaDB using credentials from .streamlit/secrets.toml"""
    return mysql.connector.connect(**st.secrets["mariadb"]) # dict unpack