import os
from dotenv import load_dotenv

import streamlit as st

load_dotenv()

# --- ADMIN CREDENTIALS ---
# Prioritizes: Streamlit Secrets -> .env/Env Vars -> Defaults
ADMIN_USER = st.secrets.get("ADMIN_USER") or os.getenv("ADMIN_USER") or "vantage_admin"
ADMIN_PASS = st.secrets.get("ADMIN_PASS") or os.getenv("ADMIN_PASS") or "architect_2024"
ADMIN_EMAIL = st.secrets.get("ADMIN_EMAIL") or os.getenv("ADMIN_EMAIL") or "admin@vantagepoint.ai"

# --- QUOTA SETTINGS (GUEST) ---
GUEST_MAX_SESSIONS = 10
GUEST_DAILY_SESSIONS = 2
GUEST_TOKEN_LIMIT = 3000

# --- AUDIT SETTINGS ---
AUDIT_THRESHOLD = 4  # Score below this means no auto-extension
