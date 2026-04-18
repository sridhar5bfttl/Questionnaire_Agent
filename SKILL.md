# Architectural Patterns & Agent Skills

This document defines the skills and implementation patterns required to maintain and extend **Vantage Point AI**. It is intended for developers continuing work on this project.

---

## 1. Streamlit UI Architecture
- **Multi-Page Layout**: Logic split across `app.py` (Main Chat) and `pages/` (Historical Review). Multi-page state is shared globally via `st.session_state`.
- **Dynamic Elements**: `st.chat_message` for history, `st.divider()` and `st.columns` for phase-specific UI (Save/Deep Dive buttons).
- **Interactive Analytics**: Plotly charts in the Dashboard for token timelines and cumulative cost visualization.
- **Starter Prompt Guard**: Starter prompts render ONLY if the conversation is empty (`not st.session_state.messages`). This is the critical guard that enables session resumption without showing irrelevant greetings.

## 2. Agent Orchestration (Multi-Agent Pattern)
The application uses two distinct agent roles:
1. **The Consultant (LLMClient)**:
   - Handles the main conversational loop.
   - Responsible for phase transitions (Greeting → Probing → Summary).
   - Generates the primary technical recommendation.
2. **The Auditor (AuditorAgent)**:
   - Evaluates the "Consultant's" performance (Scoring 1-10).
   - Generates compact conversation titles for the DB.
   - Calculates costs based on token usage (GPT-5.1 pricing model).
   - Extracts structured technical patterns (Category, Confidence, Rationale) from raw summary text.

## 3. 3-Tier API Key Resolution
All agents resolve the API key using this prioritized pattern:
```python
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or st.session_state.get("openai_api_key")
```
- **Tier 1 (`st.secrets`)**: Streamlit Cloud deployment. Safest, most secure.
- **Tier 2 (`os.getenv`)**: Local development via `.env` and `python-dotenv`.
- **Tier 3 (`st.session_state`)**: Template/clone users who enter their key in the sidebar UI.

## 4. Session Resumption Pattern
This is the core persistence and UX innovation. The end-to-end flow is:
1. **History Dashboard**: User clicks "🚀 Resume Conversation".
2. `st.session_state.resume_session_id` is set and `st.switch_page("app.py")` is called.
3. **`app.py` Startup Check**: The resume flag is detected.
4. `get_session_messages()` and `get_all_sessions()` fetch the full context from SQLite.
5. `load_session_state()` injects messages, tokens, and phase into `st.session_state`.
6. **Safety Phase Check**: `load_session_state` ensures phase is never `GREETING` if messages exist.
7. **Save Upsert**: When saving a resumed session, `current_session_id` from state is passed to `save_chat_session()`, which performs an UPDATE rather than an INSERT.

## 5. Persistence & Data Integrity
- **SQLite Mapping**:
  - `sessions`: High-level metadata, titles, audit scores, `current_phase`, `is_active`.
  - `messages`: Raw conversational transcript (cleared and re-inserted on upsert).
  - `assessments`: Structured technical outcomes.
- **Upsert Pattern**: `save_chat_session(session_id=...)` triggers an UPDATE path.
  - Old messages are deleted with `DELETE FROM messages WHERE session_id = ?`.
  - The full new message list is re-inserted.
- **Dictionary Conversion**: Always convert `sqlite3.Row` to `dict` in fetch layer.
- **Soft Delete**: Use `is_active` flag (1/0) to hide without deleting.

## 6. Full-Text Keyword Search Pattern
The `search_sessions(query)` function uses a two-pass SQL approach:
1. **Pass 1 (Session-level)**: LIKE search on `sessions.title` and `sessions.audit_feedback`. Returns a formatted `match_snippet` to show context.
2. **Pass 2 (Message-level)**: LIKE search on `messages.content` via a JOIN, extracting a 80-character window around the match.
3. **Deduplication**: Results from both passes are merged and deduplicated by `session_id`, with session-level matches taking priority.
- The UI displays a `💡 Match:` snippet below the selected session to give immediate context before resuming.

## 7. Precise Activity Tracking (Active Duration)
To solve the problem of inflated duration in resumed sessions, the `get_session_duration()` skill uses **Burst Analysis**:
- **Algorithm**: Fetches all timestamps, then iterates to sum only the gaps that are **less than 30 minutes**.
- **Resumption Handling**: Large gaps (e.g., 6 hours) between sessions are ignored, accurately reflecting only active conversation time.
- **Micro-Adjustment**: Adds a 1-minute floor for the initial setup time.
- **High-Res Timestamps**: All messages now capture `HH:MM:SS.mmm` (milliseconds) in the UI and full microsecond ISO format in the database to ensure stable ordering and precise audit trails.

## 8. Cost Tracking (The GPT-5.1 Pattern)
- Accumulate in session state: `total_input_tokens` and `total_output_tokens`.
- Apply hypothetical pricing in the Save process:
  - **Input**: $0.05 / 1k tokens
  - **Output**: $0.15 / 1k tokens

## 7. PDF Generation (Unicode-Safe Pattern)
- Use `fpdf2` for report generation.
- **Critical**: Always wrap all text through `sanitize_text()` before passing to any FPDF method.
- `sanitize_text()` maps common Unicode characters (en-dash, smart quotes, bullets) to their Latin-1 equivalents, with a final `.encode('latin-1', 'replace')` fallback.
- Output must be cast to `bytes` before being passed to `st.download_button()`.

## 8. Technical Extraction Logic
- Free-form text summaries from the LLM must be "structured" for the dashboard.
- **Extraction Flow**:
  1. Detect `SUMMARY` phase.
  2. Feed the summary text to `AuditorAgent.extract_recommendation()`.
  3. Specialized prompt returns a validated JSON object with `classification`, `confidence`, `rationale`.
  4. Persist to the `assessments` table via `save_assessment()`.

## 9. Directory Structure
```
/app/           - Logic layer
  /components/  - Modular UI (chat, prompts)
  /utils/       - Core utilities (db, state, llm, auditor, pdf)
  /prompts/     - Versioned txt templates for agents
/pages/         - Secondary app pages (Dashboard)
/data/          - SQLite persistence store
/tests/         - Logic and DB integrity tests
/assets/        - Custom CSS theme
/documentation/ - Architecture and user guides
```

## 10. Mandatory Development Workflow
To maintain project integrity:
1. **Schema Check**: When adding a new metric, update `init_db()` and run `ALTER TABLE` on the existing DB.
2. **Implementation**: Build logic in `/app/utils/` before touching the UI.
3. **3-Tier Auth**: Ensure any new agent or service uses the 3-tier key resolution pattern.
4. **Audit Integration**: Link new features to `AuditorAgent` for tracking where relevant.
5. **Dashboard Update**: Expose new data points in `pages/1_History_Dashboard.py`.
6. **Verification**: Run `pytest tests/ -v` and manually verify the Resume flow end-to-end.
