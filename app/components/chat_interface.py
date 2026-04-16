import streamlit as st

def render_chat_history(messages):
    """Render the chat history from st.session_state.messages."""
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def render_chat_input():
    """Render the chat input field and return the user input."""
    return st.chat_input("Describe your use case...")
