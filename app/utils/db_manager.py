import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("data", "conversations.db")

def init_db():
    """Initialize the database and create tables if they don't exist."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table for sessions (conversations)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            title TEXT,
            summary TEXT,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            total_cost FLOAT DEFAULT 0.0,
            audit_score INTEGER,
            audit_feedback TEXT,
            is_active INTEGER DEFAULT 1,
            current_phase TEXT DEFAULT 'GREETING'
        )
    ''')

    # Table for individual messages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')

    # Table for technical assessments/recommendations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            classification TEXT,
            confidence_score INTEGER,
            rationale TEXT,
            audit_score INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_chat_session(messages, title="New Conversation", summary=None, input_tokens=0, output_tokens=0, total_cost=0.0, audit_score=None, audit_feedback=None, current_phase="GREETING", session_id=None):
    """Save or update a chat session and its audit data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if session_id:
        # 1. Update existing session
        cursor.execute('''
            UPDATE sessions 
            SET title = ?, summary = ?, input_tokens = ?, output_tokens = ?, total_cost = ?, audit_score = ?, audit_feedback = ?, current_phase = ?, timestamp = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, summary, input_tokens, output_tokens, total_cost, audit_score, audit_feedback, current_phase, session_id))
        
        # 2. Clear old messages for this session to avoid duplicates
        cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
    else:
        # 1. Create a new session record
        cursor.execute('''
            INSERT INTO sessions (title, summary, input_tokens, output_tokens, total_cost, audit_score, audit_feedback, current_phase)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, summary, input_tokens, output_tokens, total_cost, audit_score, audit_feedback, current_phase))
        session_id = cursor.lastrowid
    
    # 3. Insert each message (new or expanded history)
    for msg in messages:
        cursor.execute(
            'INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)',
            (session_id, msg["role"], msg["content"])
        )
    
    conn.commit()
    conn.close()
    return session_id

def save_assessment(session_id, classification, confidence_score, rationale):
    """Save the final technical recommendation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO assessments (session_id, classification, confidence_score, rationale)
        VALUES (?, ?, ?, ?)
    ''', (session_id, classification, confidence_score, rationale))
    
    conn.commit()
    conn.close()

def get_all_sessions():
    """Retrieve all chat sessions summary for the dashboard that are not hidden."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions WHERE is_active = 1 ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_session_messages(session_id):
    """Retrieve all messages for a specific session including timestamps."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp ASC', (session_id,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        # Format timestamp to HH:MM for display
        try:
            d["timestamp"] = d["timestamp"][:16].split(" ")[-1]  # Extract HH:MM
        except Exception:
            d["timestamp"] = "Historical"
        result.append(d)
    return result

def get_session_assessment(session_id):
    """Retrieve assessment details for a specific session."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM assessments WHERE session_id = ?', (session_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def hide_session(session_id):
    """Mark a session as inactive (hidden from UI)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE sessions SET is_active = 0 WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()

def get_session_duration(session_id):
    """
    Calculate the duration of a session from the first to the last message timestamp.
    Returns a dict with 'started_at', 'ended_at', and 'duration_minutes'.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT MIN(timestamp), MAX(timestamp)
        FROM messages
        WHERE session_id = ?
    ''', (session_id,))
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        return {"started_at": "N/A", "ended_at": "N/A", "duration_minutes": 0}

    fmt = "%Y-%m-%d %H:%M:%S"
    try:
        start = datetime.strptime(row[0], fmt)
        end = datetime.strptime(row[1], fmt)
        duration = round((end - start).total_seconds() / 60, 1)
        return {
            "started_at": start.strftime("%d %b %Y, %H:%M"),
            "ended_at": end.strftime("%H:%M"),
            "duration_minutes": duration
        }
    except Exception:
        return {"started_at": row[0][:16], "ended_at": row[1][:16], "duration_minutes": 0}
