import sqlite3
import os
from datetime import datetime
try:
    from app.config import ADMIN_EMAIL
except ImportError:
    ADMIN_EMAIL = "admin@vantagepoint.ai"

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
            current_phase TEXT DEFAULT 'GREETING',
            user_id TEXT DEFAULT 'admin',
            is_guest INTEGER DEFAULT 0,
            session_number INTEGER DEFAULT 1
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
            burst_number INTEGER DEFAULT 1,
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

    # Table for Quota Extension Requests
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quota_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            is_guest INTEGER DEFAULT 1,
            requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'PENDING',
            request_type TEXT DEFAULT 'EXTENSION', -- 'SIGNUP' or 'EXTENSION'
            justification TEXT,
            requested_limit INTEGER DEFAULT 10,
            decision_at DATETIME,
            admin_notes TEXT
        )
    ''')

    # Table for User Activity Log (Logins, specific actions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    ''')

    # Table for Admin/System Settings (Configurable Emails, Thresholds)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Table for Identity & Access Management
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            status TEXT DEFAULT 'PENDING',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table for Individual User Quotas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_quotas (
            user_id TEXT PRIMARY KEY,
            max_sessions INTEGER DEFAULT 10,
            max_daily_sessions INTEGER DEFAULT 2,
            max_tokens INTEGER DEFAULT 5000
        )
    ''')
    
    # Initialize default admin email if not present
    cursor.execute("INSERT OR IGNORE INTO system_settings (key, value) VALUES ('admin_notification_email', ?)", (ADMIN_EMAIL,))
    cursor.execute("INSERT OR IGNORE INTO system_settings (key, value) VALUES ('audit_threshold', '4')")
    
    # Migration: Handle existing databases
    try:
        cursor.execute("SELECT user_id FROM sessions LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE sessions ADD COLUMN user_id TEXT DEFAULT 'admin'")
        cursor.execute("ALTER TABLE sessions ADD COLUMN is_guest INTEGER DEFAULT 0")
    
    try:
        cursor.execute("SELECT session_number FROM sessions LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE sessions ADD COLUMN session_number INTEGER DEFAULT 1")

    try:
        cursor.execute("SELECT burst_number FROM messages LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE messages ADD COLUMN burst_number INTEGER DEFAULT 1")

    # Migration for quota_requests
    try:
        cursor.execute("SELECT request_type FROM quota_requests LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE quota_requests ADD COLUMN request_type TEXT DEFAULT 'EXTENSION'")
        cursor.execute("ALTER TABLE quota_requests ADD COLUMN requested_limit INTEGER DEFAULT 10")

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

def save_chat_session(messages, title="New Conversation", summary=None, input_tokens=0, output_tokens=0, total_cost=0.0, audit_score=None, audit_feedback=None, current_phase="GREETING", session_id=None, user_id="admin", is_guest=0):
    """Save or update a chat session and its audit data."""
    # VERIFICATION: Calculate duration before saving
    seconds, bursts = calculate_active_duration(messages)
    m = int(seconds // 60)
    s = int(seconds % 60)
    print(f"DEBUG: Saving Session for {user_id}. Calculated Active Duration: {m}m {s}s over {bursts} burst(s).")

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
        # 1. Calculate the next session number for this user
        cursor.execute('SELECT MAX(session_number) FROM sessions WHERE user_id = ?', (user_id,))
        max_num = cursor.fetchone()[0]
        next_num = (max_num + 1) if max_num is not None else 1

        # 2. Create a new session record
        cursor.execute('''
            INSERT INTO sessions (title, summary, input_tokens, output_tokens, total_cost, audit_score, audit_feedback, current_phase, user_id, is_guest, session_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, summary, input_tokens, output_tokens, total_cost, audit_score, audit_feedback, current_phase, user_id, is_guest, next_num))
        session_id = cursor.lastrowid
    
    # 3. Insert each message (new or expanded history)
    for msg in messages:
        # Check if burst_number is already in the msg object, default to 1
        b_num = msg.get("burst_number", 1)
        ts = msg.get("raw_timestamp") or msg.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO messages (session_id, role, content, timestamp, burst_number)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, msg['role'], msg['content'], ts, b_num))
    
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

def get_all_sessions(user_id=None):
    """Retrieve all chat sessions summary for the dashboard that are not hidden, optionally filtered by user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if user_id:
        cursor.execute('SELECT * FROM sessions WHERE is_active = 1 AND user_id = ? ORDER BY timestamp DESC', (user_id,))
    else:
        cursor.execute('SELECT * FROM sessions WHERE is_active = 1 ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def search_sessions(query, user_id=None):
    """
    Search for sessions matching a keyword across titles, message content, and audit feedback.
    Returns a list of matching session dicts with an additional 'match_snippet' field.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    like_query = f"%{query}%"

    # 1. Search in Session titles and audit feedback
    sql1 = '''
        SELECT DISTINCT s.*, 
            CASE
                WHEN s.title LIKE ? THEN 'Title: ' || s.title
                WHEN s.audit_feedback LIKE ? THEN 'Audit: ' || SUBSTR(s.audit_feedback, 1, 80)
                ELSE NULL
            END as match_snippet
        FROM sessions s
        WHERE s.is_active = 1 AND (s.title LIKE ? OR s.audit_feedback LIKE ?)
    '''
    params1 = [like_query, like_query, like_query, like_query]
    if user_id:
        sql1 += ' AND s.user_id = ?'
        params1.append(user_id)
    
    sql1 += ' ORDER BY s.timestamp DESC'
    cursor.execute(sql1, params1)
    session_rows = [dict(r) for r in cursor.fetchall()]

    # 2. Search in messages content
    sql2 = '''
        SELECT DISTINCT s.*, 
            'Message: ' || SUBSTR(m.content, MAX(1, INSTR(LOWER(m.content), LOWER(?)) - 30), 80) as match_snippet
        FROM sessions s
        JOIN messages m ON m.session_id = s.id
        WHERE s.is_active = 1 AND m.content LIKE ?
    '''
    params2 = [query, like_query]
    if user_id:
        sql2 += ' AND s.user_id = ?'
        params2.append(user_id)
        
    sql2 += ' ORDER BY s.timestamp DESC'
    cursor.execute(sql2, params2)
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
    cursor.execute('SELECT role, content, timestamp, burst_number FROM messages WHERE session_id = ? ORDER BY id ASC', (session_id,))
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

def update_session_title(session_id, new_title):
    """Manually rename a session title."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE sessions SET title = ? WHERE id = ?', (new_title, session_id))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    """Get comprehensive activity stats for a specific user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Aggregates from sessions
    cursor.execute('''
        SELECT 
            COUNT(*) as total_sessions_count,
            SUM(input_tokens) as total_input,
            SUM(output_tokens) as total_output,
            MAX(timestamp) as last_active
        FROM sessions 
        WHERE user_id = ? AND is_active = 1
    ''', (user_id,))
    s_row = cursor.fetchone()
    
    # 2. Daily sessions
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT COUNT(*) FROM sessions WHERE user_id = ? AND is_active = 1 AND timestamp LIKE ?', (user_id, f"{today}%"))
    daily = cursor.fetchone()[0]
    
    # 3. Quota limits
    cursor.execute('SELECT * FROM user_quotas WHERE user_id = ?', (user_id,))
    q_row = cursor.fetchone()
    q_data = dict(q_row) if q_row else {"max_sessions": 10, "max_tokens": 5000}
    
    # 4. Total Duration (Need to sum across all user sessions)
    cursor.execute('''
        SELECT m.timestamp
        FROM messages m
        JOIN sessions s ON m.session_id = s.id
        WHERE s.user_id = ? AND s.is_active = 1
        ORDER BY m.timestamp ASC
    ''', (user_id,))
    m_rows = cursor.fetchall()
    
    conn.close()
    
    total_sec, _ = calculate_active_duration(m_rows)
    
    return {
        "total": s_row['total_sessions_count'] or 0,
        "daily": daily,
        "total_input": s_row['total_input'] or 0,
        "total_output": s_row['total_output'] or 0,
        "total_duration_seconds": total_sec,
        "max_sessions": q_data['max_sessions'],
        "max_tokens": q_data.get('max_tokens', 5000)
    }

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

# --- ADMIN & QUOTA EXTENSION UTILITIES ---

def log_activity(user_id, action, metadata=""):
    """Log a user action for auditing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_activity (user_id, action, metadata) VALUES (?, ?, ?)', 
                   (user_id, action, metadata))
    conn.commit()
    conn.close()

def create_quota_request(user_id, is_guest, justification, request_type='EXTENSION', requested_limit=10):
    """Submit a new quota or access request."""
    ensure_user(user_id)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quota_requests (user_id, is_guest, request_type, justification, requested_limit)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, int(is_guest), request_type, justification, requested_limit))
    conn.commit()
    conn.close()

def get_all_quota_requests():
    """Retrieve all pending and historical quota requests."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM quota_requests ORDER BY requested_at DESC')
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def update_quota_request(request_id, status, notes=""):
    """Approve or Reject a quota request."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE quota_requests 
        SET status = ?, admin_notes = ?, decision_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, notes, request_id))
    conn.commit()
    conn.close()

def get_system_settings():
    """Get all global key-value settings."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT key, value FROM system_settings')
    rows = cursor.fetchall()
    conn.close()
    return dict(rows)

def update_system_setting(key, value):
    """Update a global system setting."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO system_settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def get_admin_user_stats():
    """Aggregate comprehensive statistics for all users for the admin dashboard."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Base stats from sessions
    cursor.execute('''
        SELECT 
            user_id, 
            COUNT(id) as total_sessions,
            SUM(input_tokens) as total_input,
            SUM(output_tokens) as total_output,
            AVG(audit_score) as avg_audit_score,
            MAX(timestamp) as last_active
        FROM sessions
        GROUP BY user_id
    ''')
    session_stats = {row['user_id']: dict(row) for row in cursor.fetchall()}

    # 2. User account & quota data
    cursor.execute('''
        SELECT 
            u.user_id, 
            u.status, 
            u.created_at as signup_date,
            uq.max_sessions,
            qr.requested_at as last_request_date,
            qr.decision_at as last_decision_date
        FROM users u
        LEFT JOIN user_quotas uq ON u.user_id = uq.user_id
        LEFT JOIN (
            SELECT user_id, MAX(requested_at) as requested_at, MAX(decision_at) as decision_at
            FROM quota_requests
            GROUP BY user_id
        ) qr ON u.user_id = qr.user_id
    ''')
    user_data = [dict(row) for row in cursor.fetchall()]

    # 3. Merge data
    final_stats = []
    processed_uids = set()
    
    for user in user_data:
        uid = user['user_id']
        s_stats = session_stats.get(uid, {
            "total_sessions": 0, "total_input": 0, "total_output": 0, 
            "avg_audit_score": 0, "last_active": "N/A"
        })
        
        # Calculate remaining
        max_s = user['max_sessions'] or 10 # Default
        used = s_stats['total_sessions']
        
        merged = {
            **user,
            **s_stats,
            "remaining_quota": max(0, max_s - used)
        }
        final_stats.append(merged)
        processed_uids.add(uid)

    # Add any guest IDs that aren't in 'users' table but have sessions
    for uid, s_stats in session_stats.items():
        if uid not in processed_uids:
            final_stats.append({
                "user_id": uid,
                "status": "GUEST",
                "signup_date": "N/A",
                "max_sessions": 10,
                "last_request_date": "N/A",
                "last_decision_date": "N/A",
                "remaining_quota": max(0, 10 - s_stats['total_sessions']),
                **s_stats
            })

    conn.close()
    return final_stats


def get_user_quota(user_id):
    """Get the current quota limits for a specific user ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_quotas WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    else:
        # Return defaults if not specially set
        return {"user_id": user_id, "max_sessions": 10, "max_daily_sessions": 2, "max_tokens": 5000}

def set_user_quota(user_id, max_sessions, max_daily=2, max_tokens=5000):
    """Set or update a specific user's quota limits."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_quotas (user_id, max_sessions, max_daily_sessions, max_tokens)
        VALUES (?, ?, ?, ?)
    ''', (user_id, max_sessions, max_daily, max_tokens))
    conn.commit()
    conn.close()


def ensure_user(user_id):
    """Check if user exists; if not, create them with PENDING status."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, status) VALUES (?, ?)', (user_id, 'PENDING'))
    conn.commit()
    conn.close()

def get_user_status(user_id):
    """Retrieve the account status of a user (PENDING, APPROVED, REJECTED)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "GUEST"

def update_user_status(user_id, status):
    """Administrator action to approve/reject a new registration."""
    ensure_user(user_id)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET status = ? WHERE user_id = ?', (status, user_id))
    conn.commit()
    conn.close()

def get_pending_users():
    """Get all users waiting for initial registration approval."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE status = 'PENDING' ORDER BY created_at DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

