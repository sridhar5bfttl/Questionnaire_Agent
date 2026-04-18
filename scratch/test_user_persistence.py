import sqlite3
import os
import sys
from datetime import datetime

# Setup
sys.path.append(os.getcwd())
from app.utils.db_manager import init_db, save_chat_session, get_all_sessions

def test_save_and_retrieve():
    init_db()
    
    uid = "test_user_unique"
    messages = [{"role": "user", "content": "hello", "raw_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}]
    
    print(f"Saving session for {uid}...")
    sid = save_chat_session(messages, "Test Title", "Summ", 10, 20, 0.01, 8, "Good", "PROBING", None, uid, 1)
    print(f"Saved SID: {sid}")
    
    print("Retrieving sessions...")
    sessions = get_all_sessions(user_id=uid)
    print(f"Total found for {uid}: {len(sessions)}")
    
    if len(sessions) > 0:
        print("✅ SUCCESS: Session saved and retrieved.")
    else:
        print("❌ FAILURE: Session missing.")

if __name__ == "__main__":
    test_save_and_retrieve()
