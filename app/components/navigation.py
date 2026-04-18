import streamlit as st

def sidebar_nav():
    with st.sidebar:
        st.page_link("app.py", label="Vantage Point AI", icon="🎯")
        st.page_link("pages/1_History_Dashboard.py", label="History Dashboard", icon="📜")
