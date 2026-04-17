import sys
import os
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.db_manager import get_all_sessions, hide_session, save_chat_session, init_db

def verify_soft_delete():
    print("Initializing DB...")
    init_db()
    
    # Save a test session
    print("Saving test session...")
    session_id = save_chat_session(
        messages=[{"role": "user", "content": "Delete me test"}],
        title="Session to Hide"
    )
    
    # Check if it appears in all sessions
    sessions = get_all_sessions()
    titles = [s['title'] for s in sessions]
    print(f"Initial session titles: {titles}")
    assert "Session to Hide" in titles
    
    # Hide the session
    print(f"Hiding session ID {session_id}...")
    hide_session(session_id)
    
    # Check if it is now excluded
    sessions_after = get_all_sessions()
    titles_after = [s['title'] for s in sessions_after]
    print(f"Session titles after hiding: {titles_after}")
    
    if "Session to Hide" not in titles_after:
        print("SUCCESS: Session is hidden from the list.")
    else:
        print("FAILURE: Session still appears in the list.")

if __name__ == "__main__":
    verify_soft_delete()
