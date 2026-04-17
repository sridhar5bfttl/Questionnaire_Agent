# Architectural Patterns & Agent Skills

This document defines the skills and implementation patterns required to maintain and expand **Vantage Point AI**.

---

## 1. Streamlit UI Architecture
- **Multi-Page Layout**: Logic is split across `app.py` (Main Chat) and the `pages/` directory (Historical Review). Multi-page state is shared globally.
- **Dynamic Elements**: Use `st.chat_message` for history and `st.divider()` with `st.columns` for phase-specific UI components (e.g., Save/Deep Dive buttons).
- **Interactive Metrics**: The Dashboard uses `st.metric` and `st.tabs` to display structured audit data.

## 2. Agent Orchestration (Multi-Agent Pattern)
The application utilizes two distinct agent roles:
1. **The Consultant (LLMClient)**: 
   - Handles the main conversational loop.
   - Responsible for phase transitions (Greeting -> Probing -> Summary).
   - Generates the primary technical recommendation.
2. **The Auditor (AuditorAgent)**:
   - Evaluates the "Consultant's" performance (Scoring 1-10).
   - Generates compact conversation titles for the DB.
   - Calculates costs based on token usage.
   - Extracts structured technical patterns (Category, Confidence) from raw summary text.

## 3. Persistence & Data Integrity
- **SQLite Mapping**:
  - `sessions`: High-level metadata, titles, and audit scores.
  - `messages`: Raw conversational transcript.
  - `assessments`: Structured technical outcomes extracted from summaries.
- **Dictionary Conversion Pattern**: Always convert `sqlite3.Row` objects to standard Python `dict` in the fetch layer (`db_manager.py`) to ensure compatibility with Pandas and Streamlit serialization.
- **Soft Delete Pattern**: Use an `is_active` integer flag (1/0) to hide data from the UI while preserving the audit trail in the backend.

## 4. Cost Tracking (The GPT-5.1 Pattern)
- Capture `token_usage` metadata from the LangChain response object.
- Accumulate `total_input_tokens` and `total_output_tokens` in the session state.
- Apply hypothetical pricing during the Save process:
  - **Input**: $0.05 / 1k tokens
  - **Output**: $0.15 / 1k tokens

## 5. Technical Extraction Logic
- Free-form text summaries from the LLM must be "structured" for the dashboard.
- **Extraction Flow**: 
  1. Detect `SUMMARY` phase.
  2. Feed the summary text to the `AuditorAgent`.
  3. Uses a specialized recursive prompt to return a JSON object with `classification`, `confidence`, and `rationale`.
  4. Persist to the `assessments` table.

## 6. Directory Structure
- `/app/`: Logic layer.
  - `/app/components/`: Modular UI (chat, prompts).
  - `/app/utils/`: Core utilities (`db_manager.py`, `auditor_agent.py`, `llm_client.py`).
  - `/app/prompts/`: Versioned txt templates for agents.
- `/pages/`: Secondary application pages (Dashboards, Analytics).
- `/data/`: SQLite persistence store.
- `/tests/`: Logic and DB integrity tests.

## 7. Mandatory Development Workflow
To maintain project integrity, follow these steps:
1. **Schema Check**: If adding a new metric, update `init_db()` and run `ALTER TABLE` manually if data preservation is needed.
2. **Implementation**: Build logic in `/app/utils/` before touching the UI.
3. **Audit Integration**: Ensure new features are linked to the `AuditorAgent` for tracking.
4. **Dashboard Update**: Update `pages/1_History_Dashboard.py` to expose any new data points.
5. **Verification**: Run `pytest` and verify the multi-page navigation works without `KeyError`.
