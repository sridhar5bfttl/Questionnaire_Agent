import streamlit as st
from datetime import datetime
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
    
    if "total_input_tokens" not in st.session_state:
        st.session_state.total_input_tokens = 0
    
    if "total_output_tokens" not in st.session_state:
        st.session_state.total_output_tokens = 0
    
    if "session_saved" not in st.session_state:
        st.session_state.session_saved = False
    
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    
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
    """Add a message to the chat history with a timestamp. Marks session as unsaved."""
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    # Any new message makes this session "dirty" — needs saving on exit/reset
    st.session_state.session_saved = False

def get_messages():
    """Return the chat history."""
    return st.session_state.messages

def load_session_state(session_id, messages, metadata):
    """Inject historical session data into st.session_state."""
    st.session_state.current_session_id = session_id
    # When loading from DB, messages may not have timestamps - derive from DB or mark as "Historical"
    for msg in messages:
        if "timestamp" not in msg:
            msg["timestamp"] = msg.get("timestamp", "Historical")
    st.session_state.messages = messages
    st.session_state.total_input_tokens = metadata.get("input_tokens", 0)
    st.session_state.total_output_tokens = metadata.get("output_tokens", 0)
    st.session_state.session_saved = True # Prevent immediate auto-save loop
    
    # Attempt to restore the phase
    phase_str = metadata.get("current_phase", "GREETING")
    try:
        st.session_state.phase = ChatPhase[phase_str]
    except KeyError:
        st.session_state.phase = ChatPhase.SUMMARY if len(messages) > 10 else ChatPhase.PROBING
    
    # Safety: If we have messages, we shouldn't be in GREETING phase
    if st.session_state.phase == ChatPhase.GREETING and len(messages) > 0:
        st.session_state.phase = ChatPhase.PROBING
