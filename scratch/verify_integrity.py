import sys
import os
import sqlite3
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.db_manager import get_all_sessions, init_db

def check_db_integrity():
    init_db()
    sessions = get_all_sessions()
    print(f"Total sessions in DB: {len(sessions)}")
    
    for i, s in enumerate(sessions):
        print(f"Session {i+1}:")
        print(f"  Title: {s['title']}")
        print(f"  Cost: {s['total_cost']}")
        print(f"  Audit Score: {s['audit_score']}")
        # Check for expected keys
        expected_keys = ['title', 'summary', 'input_tokens', 'output_tokens', 'total_cost', 'audit_score', 'audit_feedback']
        missing = [k for k in expected_keys if k not in s]
        if missing:
            print(f"  ERROR: Missing keys: {missing}")
        else:
            print("  Integrity Check: PASSED")

if __name__ == "__main__":
    check_db_integrity()
