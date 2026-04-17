import pytest
import os
import sqlite3
from app.utils.db_manager import init_db, save_chat_session, save_assessment, DB_PATH

@pytest.fixture
def temp_db(tmp_path):
    """Fixture to create a temporary database for testing."""
    test_db_dir = tmp_path / "data"
    test_db_dir.mkdir()
    test_db_path = test_db_dir / "test_conversations.db"
    
    # Mock the DB_PATH for tests
    import app.utils.db_manager
    original_path = app.utils.db_manager.DB_PATH
    app.utils.db_manager.DB_PATH = str(test_db_path)
    
    init_db()
    yield test_db_path
    
    # Restore original path
    app.utils.db_manager.DB_PATH = original_path

def test_init_db(temp_db):
    """Verify tables are created correctly."""
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    
    # Check for sessions table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions';")
    assert cursor.fetchone() is not None
    
    # Check for messages table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages';")
    assert cursor.fetchone() is not None
    
    conn.close()

def test_save_chat_session(temp_db):
    """Verify session and messages are saved with auditing data."""
    messages = [
        {"role": "user", "content": "How are you?"},
        {"role": "assistant", "content": "I am an AI assistant."}
    ]
    
    session_id = save_chat_session(
        messages, 
        summary="Test Summary",
        input_tokens=100,
        output_tokens=200,
        total_cost=0.045,
        audit_score=9,
        audit_feedback="Great conversation"
    )
    assert session_id is not None
    
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT summary, input_tokens, total_cost, audit_score FROM sessions WHERE id = ?", (session_id,))
    result = cursor.fetchone()
    assert result[0] == "Test Summary"
    assert result[1] == 100
    assert result[2] == 0.045
    assert result[3] == 9
    
    cursor.execute("SELECT role, content FROM messages WHERE session_id = ?", (session_id,))
    saved_messages = cursor.fetchall()
    assert len(saved_messages) == 2
    assert saved_messages[0][0] == "user"
    
    conn.close()

def test_save_assessment(temp_db):
    """Verify technical assessment is saved."""
    session_id = save_chat_session([])
    save_assessment(session_id, "GenAI", 95, "Strong case for RAG")
    
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT classification, confidence_score FROM assessments WHERE session_id = ?", (session_id,))
    result = cursor.fetchone()
    assert result[0] == "GenAI"
    assert result[1] == 95
    
    conn.close()
