import sys
import os
import streamlit as st
import sqlite3

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.db_manager import init_db, save_chat_session, get_session_messages
from app.utils.state import init_state, load_session_state

def test_resume_flow():
    print("Testing Resume Flow logic...")
    init_db()
    
    # 1. Create a dummy session
    msgs = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi!"}]
    session_id = save_chat_session(msgs, title="Test Resume", current_phase="PROBING")
    print(f"Created session {session_id}")

    # 2. Simulate the resume flag in session_state
    st.session_state.resume_session_id = session_id
    
    # 3. Simulate App logic
    try:
        # Check if functions imported in app.py are available
        import app
        print("SUCCESS: app.py loaded without immediate import errors.")
        
        # Manually run the load logic that was in app.py
        if "resume_session_id" in st.session_state:
            rid = st.session_state.resume_session_id
            h_msgs = get_session_messages(rid)
            load_session_state(rid, h_msgs, {"current_phase": "PROBING", "title": "Test Resume"})
            print("SUCCESS: load_session_state executed successfully.")
            
    except Exception as e:
        print(f"FAILURE during resume flow test: {e}")

if __name__ == "__main__":
    test_resume_flow()
