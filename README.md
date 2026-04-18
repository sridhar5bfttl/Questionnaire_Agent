# Vantage Point AI

An enterprise-grade **Strategic Assessment Platform** built with Streamlit and LangChain. It guides users through a structured diagnostic to classify their business use case and recommend the optimal technical architecture—**RPA, ML, DL, NLP, or GenAI**.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 **AI Diagnostic Engine** | Multi-turn conversation to classify use cases with 0-100% confidence scores |
| 🔍 **Auditor Agent** | Independent quality score (1-10), cost estimate, and actionable feedback per session |
| 💾 **Session Persistence** | Full SQLite persistence with conversation transcripts and technical assessments |
| 🚀 **Session Resumption** | Pick up any historical conversation exactly where you left off |
| 📊 **Analytics Dashboard** | Interactive Plotly charts for token usage and cumulative GPT-5.1 cost tracking |
| 📄 **PDF Reports** | Professional consolidated reports including transcript, audit, and resource usage |
| 🎨 **Glassmorphism UI** | Premium custom CSS theme for a modern, enterprise look |
| 🔑 **3-Tier Auth** | Supports Streamlit Secrets, `.env`, and UI key input for any deployment |
| 🛡️ **Identity Gatekeeper** | Tabbed Login/Signup interface with Guest mode access |
| 📈 **Admin Dashboard** | Global user intelligence, approval queues, and engagement vs. quality matrix |
| 🚦 **Dynamic Quotas** | Automatic redirection to the Access & Quota portal for limit extensions |
| 🗑️ **Soft Delete** | Hide sessions from the UI without losing audit data |

---

## 🏗️ Project Structure

```
Questionnaire_Agent/
├── app.py                      # Main Streamlit chat interface
├── pages/
│   ├── 1_History_Dashboard.py # Analytics & history viewer
│   ├── 2_Admin_Dashboard.py   # Global user intelligence & quota approvals
│   └── _Request_Access.py     # Hidden Access & Quota portal
├── app/
│   ├── components/             # Reusable UI components
│   ├── prompts/                # Agent system prompt templates
│   └── utils/
│       ├── db_manager.py       # SQLite persistence (with upsert & phase tracking)
│       ├── state.py            # Session state management & resumption
│       ├── llm_client.py       # LangChain GPT-4o integration
│       ├── auditor_agent.py    # Quality scoring & cost tracking agent
│       └── pdf_generator.py   # Unicode-safe PDF report generator
├── assets/
│   └── custom_styles.css       # Glassmorphism theme
├── documentation/
│   ├── architecture.md         # System architecture & data flow
│   └── user_guide.md           # End-user guide
├── tests/                      # Automated test suite
├── DEPLOY.md                   # Deployment & configuration guide
└── data/
    └── conversations.db        # Local SQLite database (Sessions, Users, Quotas)
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- OpenAI API Key (with GPT-4o access)

### 1. Clone the Repository
```bash
git clone https://github.com/sridhar5bfttl/Questionnaire_Agent.git
cd Questionnaire_Agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Your API Key
**Option A: Local (`.env` file)**
```
OPENAI_API_KEY=your_api_key_here
```
**Option B: Streamlit Cloud (Secrets)**
```toml
OPENAI_API_KEY = "your_api_key_here"
```
**Option C: UI Input**
Run the app and enter the key in the sidebar when prompted.

### 4. Run the Application
```bash
streamlit run app.py
```

### 5. Run Tests
```bash
pytest tests/ -v
```

---

## 🚀 Deployment

For full deployment options (Streamlit Cloud, GitHub Codespaces, Local), see **[DEPLOY.md](DEPLOY.md)**.

---

## 🔄 How to Resume a Conversation

1. Navigate to the **History Dashboard** page.
2. Select a previous session from the sidebar.
3. Click **🚀 Resume Conversation**.
4. Continue your conversation seamlessly—the AI remembers all context.

---

## 📐 Architecture

The application uses a **Dual-Agent + State-Machine** pattern:

1. **Consultant Agent** (GPT-4o): Manages the diagnostic conversation and phase transitions.
2. **Auditor Agent** (GPT-4o-mini): Post-session quality scoring, title generation, and cost calculation.

Conversation phases: `GREETING → PROBING → SUMMARY → FEEDBACK → DEEP_DIVE`

For full technical details, see **[architecture.md](documentation/architecture.md)**.

---

## 📊 Database
```bash
# View all saved sessions
sqlite3 data/conversations.db "SELECT id, title, audit_score, current_phase FROM sessions;"

# View assessments
sqlite3 data/conversations.db "SELECT * FROM assessments;"
```
