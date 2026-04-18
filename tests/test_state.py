import pytest
import streamlit as st
from app.utils.state import (
    ChatPhase, init_state, update_phase, add_message, get_messages,
    load_session_state
)


# --- Helpers ---
def clear_and_init():
    st.session_state.clear()
    init_state()


# --- Init Tests ---

def test_init_state_creates_all_keys():
    """Test that all session state variables are initialized with correct defaults."""
    clear_and_init()
    assert "messages" in st.session_state
    assert "phase" in st.session_state
    assert "current_session_id" in st.session_state
    assert "total_input_tokens" in st.session_state
    assert "total_output_tokens" in st.session_state
    assert "session_saved" in st.session_state
    assert "user_data" in st.session_state
    assert st.session_state.phase == ChatPhase.GREETING
    assert st.session_state.current_session_id is None
    assert st.session_state.session_saved is False


# --- Phase Tests ---

def test_update_phase_to_probing():
    """Test phase transitions from Greeting to Probing."""
    clear_and_init()
    update_phase(ChatPhase.PROBING)
    assert st.session_state.phase == ChatPhase.PROBING

def test_update_phase_to_summary():
    """Test phase transitions from Probing to Summary."""
    clear_and_init()
    update_phase(ChatPhase.SUMMARY)
    assert st.session_state.phase == ChatPhase.SUMMARY


# --- Message Tests ---

def test_add_message_adds_to_history():
    """Test message addition to chat history."""
    clear_and_init()
    add_message("user", "Hello, what is ML?")
    assert len(st.session_state.messages) == 1
    assert st.session_state.messages[0]["role"] == "user"
    assert st.session_state.messages[0]["content"] == "Hello, what is ML?"

def test_get_messages_returns_history():
    """Test that get_messages returns the current history."""
    clear_and_init()
    add_message("user", "Msg 1")
    add_message("assistant", "Reply 1")
    msgs = get_messages()
    assert len(msgs) == 2


# --- Session Resumption Tests ---

def test_load_session_state_populates_messages():
    """Test that load_session_state correctly injects historical messages."""
    clear_and_init()
    historical = [
        {"role": "user", "content": "Resume from here."},
        {"role": "assistant", "content": "Noted, continuing the analysis."}
    ]
    load_session_state(42, historical, {"input_tokens": 500, "output_tokens": 300, "current_phase": "PROBING"})
    assert st.session_state.current_session_id == 42
    assert len(st.session_state.messages) == 2
    assert st.session_state.total_input_tokens == 500
    assert st.session_state.total_output_tokens == 300
    assert st.session_state.phase == ChatPhase.PROBING
    assert st.session_state.session_saved is True  # Must be True to avoid re-triggering auto-save

def test_load_session_state_overrides_greeting_phase():
    """Test that load_session_state never leaves us in GREETING if history exists."""
    clear_and_init()
    historical = [{"role": "user", "content": "Old message"}]
    # Simulate a case where phase was saved as GREETING
    load_session_state(99, historical, {"current_phase": "GREETING"})
    # Safety check must promote it to PROBING
    assert st.session_state.phase != ChatPhase.GREETING

def test_load_session_state_restores_summary_phase():
    """Test that a completed session (SUMMARY/FEEDBACK) restores to SUMMARY."""
    clear_and_init()
    historical = [{"role": "user", "content": "Old msg"}]
    load_session_state(12, historical, {"current_phase": "SUMMARY"})
    assert st.session_state.phase == ChatPhase.SUMMARY
