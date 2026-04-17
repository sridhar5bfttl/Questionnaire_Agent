# Project: Vantage Point AI (with Persistence & Auditing)

## Description
The aim of this project is to classify business use cases based on a sequence of diagnostic questions to determine the best technical solution (RPA, ML, DL, NLP, GenAI).

---

## 1. Interaction Flow

### Greetings
1. Chat agent greets the user and asks for a use case description.
2. Provides 5 AI-powered starter prompts for a quick start.

### Diagnostic Probing
1. Agent probes for input data types (Stuctured/Unstructured), volumes, quality, and business goals.
2. Dynamically adjusts questions based on the identified technical domain.
3. Rephrases the user's input for confirmation before providing a formal summary.

### Summary & Technical Recommendation [PHASE_CHANGE: SUMMARY]
1. Provides a structured list of possible solutions with confidence scores (0-100%).
2. Offers a detailed technical rationale for each recommendation.

---

## 2. Intelligence & Auditing

### Auditor Agent
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
2. **Auto-Save on Reset**: Any unsaved session is automatically audited and persisted before common state reset.
3. **Soft Delete**: "Hide from List" functionality to remove sessions from the UI while maintaining audit logs in the backend.

### History Dashboard & Reporting
1. Dedicated multi-page interface (`pages/1_History_Dashboard.py`).
2. **Global Analytics**: Token Usage Timelines and Cumulative Budget Utilization (via Plotly).
3. **Session Review**: Drill-down with full transcripts and AI audit feedback.
4. **Professional Export**: Consolidated PDF reports including transcript, audit, and resource usage.

---

## 4. Architecture
- **Framework**: Streamlit (Main chat UI) + custom CSS (Glassmorphism).
- **Core Engine**: LangChain + GPT-4o.
- **Persistence**: SQLite (db_manager.py).
- **Orchestration**: Multi-Agent pattern (Consultant + Auditor).
- **State Management**: Complex `st.session_state` with Phase Tracking and Auto-save logic.
