import pytest
import os
import sqlite3
from app.utils.db_manager import (
    init_db, save_chat_session, save_assessment,
    get_all_sessions, get_session_messages, get_session_assessment,
    hide_session, DB_PATH
)

@pytest.fixture
def temp_db(tmp_path):
    """Fixture to create a temporary database for testing."""
    test_db_dir = tmp_path / "data"
    test_db_dir.mkdir()
    test_db_path = test_db_dir / "test_conversations.db"

    import app.utils.db_manager
    original_path = app.utils.db_manager.DB_PATH
    app.utils.db_manager.DB_PATH = str(test_db_path)

    init_db()
    yield test_db_path

    app.utils.db_manager.DB_PATH = original_path


# --- Schema Tests ---

def test_init_db_creates_tables(temp_db):
    """Verify all required tables are created on init."""
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    for table in ["sessions", "messages", "assessments"]:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
        assert cursor.fetchone() is not None, f"Table '{table}' not found"
    conn.close()

def test_init_db_sessions_has_phase_column(temp_db):
    """Verify the current_phase column exists for session resumption."""
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(sessions);")
    columns = [row[1] for row in cursor.fetchall()]
    assert "current_phase" in columns, "current_phase column missing from sessions table"
    assert "is_active" in columns, "is_active column missing from sessions table"
    conn.close()


# --- Create Tests ---

def test_save_chat_session_creates_new_record(temp_db):
    """Verify a new session is created with auditing and phase data."""
    messages = [
        {"role": "user", "content": "What is RPA?"},
        {"role": "assistant", "content": "RPA stands for Robotic Process Automation."}
    ]
    session_id = save_chat_session(
        messages,
        title="RPA Discovery",
        summary="User asked about RPA",
        input_tokens=100,
        output_tokens=200,
        total_cost=0.035,
        audit_score=8,
        audit_feedback="Excellent clarity.",
        current_phase="SUMMARY"
    )
    assert session_id is not None

    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute("SELECT title, current_phase, audit_score, is_active FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    assert row[0] == "RPA Discovery"
    assert row[1] == "SUMMARY"
    assert row[2] == 8
    assert row[3] == 1  # active
    conn.close()


# --- Upsert / Resume Tests ---

def test_save_chat_session_updates_existing_record(temp_db):
    """Verify that passing session_id updates rather than duplicates a session."""
    messages = [{"role": "user", "content": "Tell me about ML."}]
    session_id = save_chat_session(messages, title="ML Session", current_phase="PROBING")

    # Simulate resuming: add a message and re-save
    extended_messages = messages + [{"role": "assistant", "content": "ML is machine learning."}]
    returned_id = save_chat_session(
        extended_messages,
        title="ML Session (Resumed)",
        current_phase="SUMMARY",
        session_id=session_id
    )
    assert returned_id == session_id, "Upsert should return same session_id"

    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()

    # Only 1 session should exist (no duplicate)
    cursor.execute("SELECT COUNT(*) FROM sessions WHERE id = ?", (session_id,))
    assert cursor.fetchone()[0] == 1

    # Title and phase should be updated
    cursor.execute("SELECT title, current_phase FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    assert row[0] == "ML Session (Resumed)"
    assert row[1] == "SUMMARY"

    # Messages should reflect the extended set (no old stale messages)
    cursor.execute("SELECT COUNT(*) FROM messages WHERE session_id = ?", (session_id,))
    assert cursor.fetchone()[0] == 2
    conn.close()


# --- Fetch Tests ---

def test_get_all_sessions_excludes_hidden(temp_db):
    """Verify that hidden sessions are excluded from the listing."""
    sid1 = save_chat_session([], title="Active Session")
    sid2 = save_chat_session([], title="Hidden Session")
    hide_session(sid2)

    sessions = get_all_sessions()
    ids = [s["id"] for s in sessions]
    assert sid1 in ids
    assert sid2 not in ids

def test_get_session_messages_returns_ordered_history(temp_db):
    """Verify messages are returned in chronological order."""
    msgs = [
        {"role": "user", "content": "First message"},
        {"role": "assistant", "content": "First reply"},
        {"role": "user", "content": "Second message"},
    ]
    sid = save_chat_session(msgs, title="Order Test")
    fetched = get_session_messages(sid)
    assert len(fetched) == 3
    assert fetched[0]["content"] == "First message"
    assert fetched[2]["content"] == "Second message"

def test_save_and_retrieve_assessment(temp_db):
    """Verify technical assessment is correctly saved and retrieved."""
    sid = save_chat_session([], title="Assessment Test")
    save_assessment(sid, "GenAI", 92, "Strong NLP fit with LLM pattern.")

    assessment = get_session_assessment(sid)
    assert assessment is not None
    assert assessment["classification"] == "GenAI"
    assert assessment["confidence_score"] == 92
    assert "NLP" in assessment["rationale"]
