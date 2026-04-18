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

def calculate_active_duration(messages):
    """
    Core logic to calculate active duration from a list of message objects.
    Returns (total_seconds, burst_count).
    """
    if not messages:
        return 0.0, 0
    
    fmt_full = "%Y-%m-%d %H:%M:%S.%f"
    fmt_short = "%Y-%m-%d %H:%M:%S"
    timestamps = []
    
    for m in messages:
        # Handle dict format (from state)
        if isinstance(m, dict):
            raw_ts = m.get("raw_timestamp")
        # Handle tuple/Row format (from DB)
        elif isinstance(m, (tuple, sqlite3.Row)):
            raw_ts = m[0]
        else:
            continue
            
        if not raw_ts: continue
        
        try:
            if "." in raw_ts:
                timestamps.append(datetime.strptime(raw_ts[:26], fmt_full))
            else:
                timestamps.append(datetime.strptime(raw_ts[:19], fmt_short))
        except:
            continue

    if not timestamps:
        return 0.0, 0

    timestamps.sort()
    total_seconds = 0.0
    GAP_THRESHOLD = 30 * 60  # 30 minutes
    burst_count = 1

    for i in range(1, len(timestamps)):
        diff = (timestamps[i] - timestamps[i-1]).total_seconds()
        if diff < GAP_THRESHOLD:
            total_seconds += diff
        else:
            burst_count += 1
    
    # Add a 10s floor per active burst
    total_seconds += (burst_count * 10)
    return total_seconds, burst_count

def save_chat_session(messages, title="New Conversation", summary=None, input_tokens=0, output_tokens=0, total_cost=0.0, audit_score=None, audit_feedback=None, current_phase="GREETING", session_id=None):
    """Save or update a chat session and its audit data."""
    # VERIFICATION: Calculate duration before saving
    seconds, bursts = calculate_active_duration(messages)
    m = int(seconds // 60)
    s = int(seconds % 60)
    print(f"DEBUG: Saving Session. Calculated Active Duration: {m}m {s}s over {bursts} burst(s).")

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
        if "raw_timestamp" in msg and msg["raw_timestamp"]:
            cursor.execute(
                'INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)',
                (session_id, msg["role"], msg["content"], msg["raw_timestamp"])
            )
        else:
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

def search_sessions(query):
    """
    Search for sessions matching a keyword across titles, message content, and audit feedback.
    Returns a list of matching session dicts with an additional 'match_snippet' field.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    like_query = f"%{query}%"

    cursor.execute('''
        SELECT DISTINCT s.*, 
            CASE
                WHEN s.title LIKE ? THEN 'Title: ' || s.title
                WHEN s.audit_feedback LIKE ? THEN 'Audit: ' || SUBSTR(s.audit_feedback, 1, 80)
                ELSE NULL
            END as match_snippet
        FROM sessions s
        WHERE s.is_active = 1 AND (
            s.title LIKE ?
            OR s.audit_feedback LIKE ?
        )
        ORDER BY s.timestamp DESC
    ''', (like_query, like_query, like_query, like_query))
    session_rows = [dict(r) for r in cursor.fetchall()]

    # Also search in messages content
    cursor.execute('''
        SELECT DISTINCT s.*, 
            'Message: ' || SUBSTR(m.content, MAX(1, INSTR(LOWER(m.content), LOWER(?)) - 30), 80) as match_snippet
        FROM sessions s
        JOIN messages m ON m.session_id = s.id
        WHERE s.is_active = 1 AND m.content LIKE ?
        ORDER BY s.timestamp DESC
    ''', (query, like_query))
    msg_rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Merge, deduplicate by session id, prefer session-level matches
    seen = {s['id'] for s in session_rows}
    for row in msg_rows:
        if row['id'] not in seen:
            session_rows.append(row)
            seen.add(row['id'])

    return session_rows

def get_session_messages(session_id):
    """Retrieve all messages for a specific session including formatted timestamps."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp ASC', (session_id,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        raw_ts = d.get("timestamp", "")
        # Preserve original DB timestamp for re-saving logic
        d["raw_timestamp"] = raw_ts
        try:
            # Flexible parsing for both YYYY-MM-DD HH:MM:SS and YYYY-MM-DD HH:MM:SS.ffffff
            if "." in raw_ts:
                dt = datetime.strptime(raw_ts[:26], "%Y-%m-%d %H:%M:%S.%f")
                d["timestamp"] = dt.strftime("%d %b %Y, %H:%M:%S.") + dt.strftime("%f")[:3]
            else:
                dt = datetime.strptime(raw_ts[:19], "%Y-%m-%d %H:%M:%S")
                d["timestamp"] = dt.strftime("%d %b %Y, %H:%M:%S.000")
        except:
            d["timestamp"] = raw_ts if raw_ts else "N/A"
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
    Calculate the active duration of a session by summing intervals between messages.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp
        FROM messages
        WHERE session_id = ?
        ORDER BY timestamp ASC
    ''', (session_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {"started_at": "N/A", "ended_at": "N/A", "duration_minutes": 0, "duration_formatted": "0s"}

    total_seconds, burst_count = calculate_active_duration(rows)

    if not rows: # Recalculate start/end for display
         return {"started_at": "N/A", "ended_at": "N/A", "duration_minutes": 0, "duration_formatted": "0s"}

    # Re-parse for formatting
    fmt_full = "%Y-%m-%d %H:%M:%S.%f"
    fmt_short = "%Y-%m-%d %H:%M:%S"
    
    def parse_ts(raw):
        try:
            return datetime.strptime(raw[:26], fmt_full) if "." in raw else datetime.strptime(raw[:19], fmt_short)
        except: return datetime.now()

    start_dt = parse_ts(rows[0][0])
    end_dt = parse_ts(rows[-1][0])

    duration_min = round(total_seconds / 60, 2)
    
    # Format as Mm Ss
    mins = int(total_seconds // 60)
    secs = int(total_seconds % 60)
    
    if mins > 0:
        duration_formatted = f"{mins}m {secs}s"
    else:
        duration_formatted = f"{secs}s"
    
    return {
        "started_at": start_dt.strftime("%d %b %Y, %H:%M:%S"),
        "ended_at": end_dt.strftime("%H:%M:%S"),
        "duration_minutes": duration_min,
        "duration_formatted": duration_formatted
    }
