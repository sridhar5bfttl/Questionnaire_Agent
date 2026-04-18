import streamlit as st

def render_chat_history(messages):
    """Render the chat history with per-message timestamps."""
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Show timestamp as a subtle caption below each message
            ts = message.get("timestamp", "")
            if ts:
                label = "You" if message["role"] == "user" else "Vantage Point AI"
                st.caption(f"🕐 {label} · {ts}")

def render_chat_input():
    """Render the chat input field and return the user input."""
    return st.chat_input("Describe your use case...")
