# System Architecture: Vantage Point AI

Vantage Point AI is a multi-agent diagnostic system built on **Streamlit**, **LangChain**, and **SQLite**. It is designed to bridge the gap between business requirements and technical solution blueprints, and to enable seamless session resumption across multiple engagements.

---

## 1. Multi-Agent Ecosystem

### A. The Consultant Agent (Orchestrator)
- **Role**: Primary user interface and diagnostic lead.
- **Responsibility**: Manages the multi-turn conversation (Greeting → Probing → Summary → Deep Dive).
- **Core Skill**: Zero-shot technical classification and dynamic question generation.

### B. The Auditor Agent (Governance)
- **Role**: Quality control, metadata extractor, and financial tracker.
- **Responsibilities**:
  - **Quality Scoring**: Evaluates conversations on a 1-10 scale.
  - **Cost Tracking**: Calculates token usage and USD costs (GPT-5.1 pricing).
  - **Intelligence Extraction**: Parses raw summaries into structured data (Category, Confidence, Rationale).
### C. The Quota Agent (Administration)
- **Role**: AI-driven administrative assistant.
- **Responsibilities**:
  - Reviews user extension requests and drafts business case justifications based on their previous chat analytics.

---

## 2. Data Flow Diagram

```mermaid
graph TD
    User([User]) <--> Auth[Identity Gatekeeper]
    Auth -- Pending / New --> Quota[Access & Quota Portal]
    Auth -- Approved / Guest --> UI[Streamlit Main Chat]
    
    subgraph "Intelligent Core"
        UI <--> LLM["LLM Client (GPT-4o)"]
        UI -- Save / Reset --> Auditor[Auditor Agent]
        Quota <--> QAgent[Quota Agent]
    end
    
    subgraph "Persistence Layer"
        Auditor -- Metadata + Phase --> SQL[(SQLite DB)]
        LLM -- Transcript --> SQL
        Auth -- User/Status --> SQL
        Quota -- Limitations/Requests --> SQL
    end
    
    subgraph "Analytics & Management"
        SQL --> Dashboard[History Dashboard]
        Dashboard -- Resume Flag --> UI
        SQL --> Admin[Admin Dashboard]
    end
```

---

## 3. Session Resumption Flow

```mermaid
sequenceDiagram
    participant User
    participant Dashboard as History Dashboard
    participant App as app.py
    participant DB as SQLite DB
    participant State as st.session_state

    User->>Dashboard: Selects a session
    User->>Dashboard: Clicks "Resume Conversation"
    Dashboard->>State: Sets resume_session_id
    Dashboard->>App: st.switch_page("app.py")
    App->>State: Detects resume_session_id flag
    App->>DB: get_session_messages(session_id)
    App->>DB: get_all_sessions() for metadata
    App->>State: load_session_state(messages, phase, tokens)
    State->>App: Clears resume flag
    App->>User: Displays full history, ready to continue
    User->>App: Sends new message
    App->>DB: save_chat_session(session_id=existing_id) [UPSERT]
```

---

## 4. 3-Tier API Key Authentication

```mermaid
flowchart LR
    A[App Starts] --> B{st.secrets has key?}
    B -- Yes --> E[Use Secrets Key]
    B -- No --> C{os.getenv has key?}
    C -- Yes --> E
    C -- No --> D{session_state has key?}
    D -- Yes --> E
    D -- No --> F[Show Sidebar Input]
    F --> G{User enters key?}
    G -- Yes --> H[Store in session_state]
    H --> E
    G -- No --> I[st.stop - App Locked]
```

---

## 5. Database Schema

The system uses a local `data/conversations.db` SQLite database with three relational tables:

| Table | Key Columns | Purpose |
|---|---|---|
| `sessions` | `id`, `title`, `current_phase`, `audit_score`, `total_cost`, `is_active` | High-level session metadata |
| `messages` | `session_id`, `role`, `content` | Full conversational transcript |
| `assessments` | `session_id`, `classification`, `confidence_score`, `rationale` | Structured technical recommendations |

---

## 6. Financial Model (GPT-5.1)

To provide "Cloud Governance" visibility, the system implements a hypothetical GPT-5.1 pricing model:
- **Input Tokens**: $0.05 per 1k tokens.
- **Output Tokens**: $0.15 per 1k tokens.
- **Reporting**: Metrics are aggregated per session and globally in the History Dashboard via Plotly charts.
