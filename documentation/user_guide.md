# User Guide: Vantage Point AI

Welcome to **Vantage Point AI**! This guide will help you navigate the application, manage your sessions, and understand how your technical assessments are stored and audited.

---

## 1. Accessing the Platform

### The Identity Gatekeeper
When you launch Vantage Point AI, you must identify yourself:
- **Existing Users**: Use the **Login** tab to access the platform immediately.
- **New Users**: Use the **Signup** tab. You will be redirected to the **Access Portal** where you must submit a usecase justification. An administrator will review and approve your account.
- **Guest Mode**: You may click "Work with Application" to test the system with a limited capacity of 10 total sessions.

### My Usage Dashboard
Once logged in, your personal dashboard appears in the sidebar:
- Tracks your active **Interaction Time**.
- Displays remaining **Session Quota** (e.g., 5/20 sessions).
- Monitors real-time **Token Consumption**.
- Provides a direct link to request a quota extension.

---

## 2. Starting an Assessment

### The Greeting Phase
When you enter the chat, you'll be greeted by the **Consultant Agent**. 
- You can either type your business problem manually in the chat box or...
- Use one of the **5 Starter Prompts** (e.g., "Automate invoice processing") to see immediate results.

### The Diagnostic Flow
The agent will ask you follow-up questions about:
- Your input data (Types, volume).
- Your desired output.
- Business constraints.
*Tip: Give detailed answers to improve the confidence score of the final recommendation.*

---

## 2. Managing Sessions

### Saving Your Work
Once the agent provides a **Technical Summary**, you will see a **💾 Save to Database (w/ Audit)** button.
- **Title Generation**: The AI will automatically generate a short title (e.g., "RPA for Finance") for your session.
- **Audit**: A secondary **Auditor Agent** will review the conversation and assign a quality score.
- **Cost Tracking**: The system will estimate the cost of the AI interaction based on the GPT-5.1 pricing model.

### Resetting & Auto-Save
If you click **"Save and New Chat"** in the sidebar:
- **Auto-Save**: If you haven't saved your current session yet, the system will **automatically** perform an audit and save it to the database before clearing the screen. This ensures no technical assessment is ever lost.

---

## 3. History & Analytics Dashboard

Navigate to the **History Dashboard** via the sidebar on the left.

### Global Metrics
At the top of the dashboard, you can see global statistics across all your sessions:
- **Total Sessions**: How many assessments you've completed.
- **Total Cost**: Cumulative cost in USD.
- **Avg Audit Score**: The average quality of your interactions.

### Session Review
Select any previous session from the sidebar to view:
- **💬 Transcript**: The full text of the conversation.
- **🎯 Technical Recommendation**: The final classification (e.g., *GenAI*), the confidence ranking, and the rationale.
- **🔍 Audit Details**: Specific feedback from the Auditor Agent and a line-item cost breakdown.

---

## 4. Cleaning Up Your History

### Hiding Sessions (Soft Delete)
If you want to declutter your list:
1. Go to the **History Dashboard**.
2. Select the session you want to remove.
3. Click **🗑️ Hide from List** in the sidebar.

*Note: The data is not deleted from the database. It is simply hidden from the UI for better focus. Hidden sessions can still be queried by database administrators for auditing purposes.*

---

## 5. Technical Support
Vantage Point AI uses a local SQLite database stored at `data/conversations.db`. If you need to move your history to another machine, simply copy this file.
