# Guest Mode Architecture

This document defines the rules, variables, and enforcement constraints for "Guest Mode" in Vantage Point AI. Any modifications to unauthenticated usage must adhere to these patterns.

## 1. Identity & State
- **State Flags**: Guest Mode is activated when `st.session_state.is_guest = True` and `st.session_state.bypass_login = True`.
- **Global ID**: Guests share a default identity: `st.session_state.user_id = "guest_default"`.
- **Anonymity Limitation**: Because guests share a single ID, they do **not** have private historical session persistence across browsers. History Dashboard data for `guest_default` is theoretically shared or ephemeral.

## 2. Hard Quotas (`app/config.py`)
Guest usage is heavily restricted to prevent abuse and API cost bleeding. Current defaults:
- `GUEST_MAX_SESSIONS = 10` (Total lifetime sessions allowed per guest identity).
- `GUEST_DAILY_SESSIONS = 2` (Max sessions per 24 hours).
- `GUEST_TOKEN_LIMIT = 3000` (Max conversational context window).

## 3. Enforcement Pattern (`app.py`)
- **Pre-Flight Checks**: Before rendering the chat interface or evaluating user input, `app.py` actively polls `get_user_stats()` against `get_user_quota()`.
- **Block & Stop**: If a limit is breached (Total Sessions, Daily Sessions, or Token Limit), the UI renders an `st.error()` message and immediately executes `st.stop()`, preventing any further LLM calls.

## 4. The Conversion Funnel
- **Purpose**: Guest mode functions as a "Trial/Demo" environment.
- **Trigger**: When a guest hits a quota block, or voluntarily wishes to unlock persistent history, they are directed to the **Request Access Portal** (`pages/requestaccess.py`).
- **Upsell Mechanism**: The UI explicitly displays: *"Guest Mode Active: Login/Signup to unlock higher quotas and persistent search history."*
- **Approval Flow**: Guests submit a Business Case. This skips the `users` table initially and logs a `SIGNUP` task in the `quota_requests` table. Only upon Admin Approval via the dashboard is their formal user record (and dedicated quotas) hydrated into the system.