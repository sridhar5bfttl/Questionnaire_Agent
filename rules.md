# Vantage Point AI - Global Agent Rules

These rules are strictly defined for LLMs and AI Agents interacting, modifying, or extending this codebase. You MUST adhere to these architectural limits and patterns.

## 1. Security & Git Push Rules
- **No Secrets Leaked**: You MUST aggressively scan `.env.example`, config files, and code for leaked credentials before initiating a `git push`.
- **Scrubbing Format**: Replace the right-hand side of any credential with `your_lowercase_key_name_here`. 
  - *Example*: `OPENAI_API_KEY=your_openai_api_key_here`, `ADMIN_USER=your_admin_user_here`.
- **3-Tier Auth**: All agents must resolve API keys using the exact pattern: `st.secrets` > `os.getenv` > `st.session_state`. Do not hardcode configurations.

## 2. UI & Navigation (Streamlit)
- **Do not use pages/ directory for Auto-Routing**: The default Streamlit sidebar navigation is permanently disabled in `.streamlit/config.toml` (`showSidebarNavigation = false`).
- **Sidebar Injection**: Navigation links are explicitly managed in `app/components/navigation.py` using `st.page_link`. Do not use Streamlit CSS hacks to hide pages.
- **Hidden Portals**: Pages like admin (`pages/admin.py`) and registration (`pages/requestaccess.py`) intentionally omit the `sidebar_nav()` injected into the main routing logic to remain hidden. Do not modify this structure to expose them in the sidebar.

## 3. Persistent Database Operations
- **Upsert Pattern**: Modifying an existing session triggers an UPDATE path (`save_chat_session(session_id=...)`). Old messages are deleted, and the new array is inserted to prevent race conditions.
- **Dictionary State**: Always convert `sqlite3.Row` objects to Python `dict` before returning them from `db_manager.py`.
- **Schema Changes**: If you add new data requirements, you MUST update `init_db()` and manually provide `ALTER TABLE` commands for backward compatibility. Never drop a table to upgrade schema.
- **Soft Deletes**: Use the `is_active = 0` flag. Never `DELETE FROM sessions`.

## 4. Multi-Agent System Constraints
- **The Consultant (`LLMClient`)**: Manages the conversational state machine (`GREETING`, `PROBING`, `SUMMARY`). Responsible for the technical recommendation.
- **The Auditor (`AuditorAgent`)**: Executes silently in the background when the user saves the chat. Handles grading (1-10), title generation, and keyword extraction.
- **Title Guard**: `auditor.generate_title()` MUST ONLY be invoked if `st.session_state.current_title` is `None`. This prevents LLMs from overwriting user-defined session names.

## 5. Analytics & Computation
- **Active Duration (Burst Analysis)**: Session duration is calculated not by `(End - Start)` which includes hours of idle time, but by "Burst Analysis". Consecutive timestamps `< 30 minutes` apart are summed together with a `10s` minimum floor per interaction. Do not alter this algorithm.
- **Cross-Joined Administration**: Admin dashboards compute live User Quotas by aggressively joining `users`, `sessions`, and `user_quotas`.

## 6. Development Workflow Pipeline
1. Build backend logic in `/app/utils/` before touching any UI component.
2. Link new LLM interaction variables to `AuditorAgent` to ensure metrics are tracked.
3. Expose new operational data points onto `pages/1_History_Dashboard.py`.
4. Run `pytest tests/ -v` and manually verify UI integrity before committing.
