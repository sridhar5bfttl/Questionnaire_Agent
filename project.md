# Project: Vantage Point AI

## Description
**Vantage Point AI** is an enterprise-grade strategic assessment platform. It classifies business use cases based on a dynamic sequence of diagnostic questions to determine the optimal technical architecture—**RPA, ML, DL, NLP, or GenAI**—and generates professional audit reports, analytics, and consolidated session histories.

---

## 1. Interaction Flow

### 1a. New Conversation
1. Agent greets the user and offers 5 AI-powered starter prompts.
2. Agent probes for input data types (Structured/Unstructured), volumes, quality, and business goals.
3. Dynamically adjusts questions based on the identified technical domain.
4. Transitions to **Summary Phase** and presents a structured list of recommended solutions with confidence scores (0-100%).
5. User can deep dive into the selected architecture.

### 1b. Resume Conversation
1. User opens the **History Dashboard** and selects a previous session.
2. User clicks **"🚀 Resume Conversation"** to return to the main chat.
3. Full conversation history and phase context are re-loaded from the database.
4. Starter prompts are **suppressed**; the AI continues where it left off.
5. Any new messages extend the same session record (via upsert, no duplicates).

---

## 2. Intelligence & Auditing

### Auditor Agent (Quality Gate)
1. **Quality Scoring**: Every saved session is analyzed (1-10) for helpfulness and technical accuracy.
2. **Title Generation**: AI generates a short (3-5 word) title for easy historical lookup.
3. **Recommendation Extraction**: Structured data (Category, Confidence, Rationale) is extracted from raw chat text for the dashboard.
4. **Audit Feedback**: Provides constructive feedback on how the conversation was handled.

### Cost Tracking (GPT-5.1 Model)
1. Tracks cumulative token usage (Input & Output) per session.
2. Calculates estimated cost based on hypothetical GPT-5.1 pricing:
   - **Input**: $0.05 / 1k tokens
   - **Output**: $0.15 / 1k tokens

---

## 3. Persistence & UI

### Data Management
1. **SQLite Backend**: Local storage for `sessions`, `messages`, and `technical_assessments`.
   - `sessions` table includes `current_phase` column for resumption support.
2. **Auto-Save on Reset**: Any unsaved session is automatically audited and persisted before state reset.
3. **Soft Delete**: "Hide from List" functionality to remove sessions from the UI while maintaining audit logs in the backend.
4. **Upsert Logic**: When a resumed session is saved, it updates the existing record (no duplicates).

### History Dashboard & Reporting
1. Dedicated multi-page interface (`pages/1_History_Dashboard.py`).
2. **Global Analytics**: Token Usage Timelines and Cumulative Budget Utilization (via Plotly).
3. **Session Review**: Drill-down with full transcripts and AI audit feedback.
4. **Professional Export**: Consolidated PDF reports including transcript, audit, and resource usage.
5. **Session Resumption**: "🚀 Resume Conversation" button to pick up any session exactly where it left off.

---

## 4. Deployment & Authentication (3-Tier API Key)
The application uses a prioritized 3-tier key resolution:
1. **`st.secrets`**: Streamlit Community Cloud.
2. **`.env`**: Local development.
3. **Sidebar UI Input**: Template/Clone users with no config.

---

## 5. Architecture
- **Framework**: Streamlit (Main chat UI) + custom CSS (Glassmorphism).
- **Core Engine**: LangChain + GPT-4o.
- **Persistence**: SQLite (`db_manager.py`) with upsert & phase-tracking support.
- **Orchestration**: Multi-Agent pattern (Consultant + Auditor).
- **State Management**: Complex `st.session_state` with Phase Tracking, Auto-save, and Session-Resume logic.
- **Reporting**: `fpdf2`-based PDF engine with Unicode sanitization.
