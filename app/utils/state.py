import streamlit as st
from enum import Enum, auto

class ChatPhase(Enum):
    GREETING = auto()
    PROBING = auto()
    SUMMARY = auto()
    FEEDBACK = auto()
    DEEP_DIVE = auto()

def init_state():
    """Initialize session state variables if they don't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "phase" not in st.session_state:
        st.session_state.phase = ChatPhase.GREETING
    
    if "user_data" not in st.session_state:
        st.session_state.user_data = {
            "description": "",
            "inputs": "",
            "outputs": "",
            "volume": "",
            "quality": "",
            "selected_solution": None,
            "feedback": None
        }

def update_phase(new_phase: ChatPhase):
    """Update the current conversation phase."""
    st.session_state.phase = new_phase

def add_message(role: str, content: str):
    """Add a message to the chat history."""
    st.session_state.messages.append({"role": role, "content": content})

def get_messages():
    """Return the chat history."""
    return st.session_state.messages
