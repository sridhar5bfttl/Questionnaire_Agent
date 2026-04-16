import pytest
from app.utils.state import ChatPhase, init_state, update_phase, add_message
import streamlit as st

def test_init_state():
    """Test that all session state variables are initialized."""
    # Mock st.session_state
    st.session_state.clear()
    init_state()
    
    assert "messages" in st.session_state
    assert "phase" in st.session_state
    assert st.session_state.phase == ChatPhase.GREETING
    assert "user_data" in st.session_state

def test_update_phase():
    """Test phase transitions."""
    st.session_state.clear()
    init_state()
    
    update_phase(ChatPhase.PROBING)
    assert st.session_state.phase == ChatPhase.PROBING

def test_add_message():
    """Test message addition to history."""
    st.session_state.clear()
    init_state()
    
    add_message("user", "Hello")
    assert len(st.session_state.messages) == 1
    assert st.session_state.messages[0]["role"] == "user"
    assert st.session_state.messages[0]["content"] == "Hello"
