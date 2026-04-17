import sys
import os
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.db_manager import init_db, save_chat_session, get_all_sessions

def verify_history_logic():
    print("Initializing test DB...")
    init_db()
    
    print("Saving test session...")
    save_chat_session(
        messages=[{"role": "user", "content": "Test History"}],
        title="Test Session Title",
        summary="Testing Dashboard Data",
        input_tokens=50,
        output_tokens=50,
        total_cost=0.01,
        audit_score=10,
        audit_feedback="Excellent data flow"
    )
    
    print("Reading sessions...")
    sessions = get_all_sessions()
    if len(sessions) > 0:
        print(f"SUCCESS: Found {len(sessions)} sessions.")
        print(f"First Session Title: {[s['title'] for s in sessions][0]}")
    else:
        print("FAILURE: No sessions found.")

if __name__ == "__main__":
    verify_history_logic()
