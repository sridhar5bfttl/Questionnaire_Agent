import os
from dotenv import load_dotenv

load_dotenv()

# --- ADMIN CREDENTIALS ---
ADMIN_USER = os.getenv("ADMIN_USER", "vantage_admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "architect_2024")

# --- QUOTA SETTINGS (GUEST) ---
GUEST_MAX_SESSIONS = 4
GUEST_DAILY_SESSIONS = 2
GUEST_TOKEN_LIMIT = 3000

# --- AUDIT SETTINGS ---
AUDIT_THRESHOLD = 4  # Score below this means no auto-extension
