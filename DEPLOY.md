# 🚀 Deploying Vantage Point AI

This guide explains how to host **Vantage Point AI** on different platforms and how to manage your OpenAI API Key securely.

---

## 🏗️ 3-Tier API Key Configuration
The application is designed to be "template-ready." It checks for an API Key in the following order:

1.  **Streamlit Secrets** (Best for Cloud Hosting)
2.  **Environment Variables** (Best for Local Development)
3.  **UI Sidebar Input** (Best for quick testing or sharing the repo template)

---

## 1. Hosting on Streamlit Community Cloud (Recommended)
This is the easiest way to share your application.

1.  **Push your code** to a GitHub repository.
2.  Go to [share.streamlit.io](https://share.streamlit.io) and connect your repository.
3.  **Configure Secrets**:
    -   In the Streamlit Cloud dashboard, go to **Settings** > **Secrets**.
    -   Add your key using this format:
        ```toml
        OPENAI_API_KEY = "your-actual-api-key-here"
        ```
4.  The application will automatically detect this secret and skip the UI login sidebar.

---

## 2. Running Locally
For developers working on the codebase.

1.  **Clone the Repository**.
2.  **Create a `.env` file** in the root directory:
    ```bash
    OPENAI_API_KEY=your_api_key_here
    ```
3.  Install dependencies: `pip install -r requirements.txt`.
4.  Run the app: `streamlit run app.py`.

> [!WARNING]
> The `.env` file is listed in `.gitignore` to prevent you from accidentally pushing your private keys to GitHub. **Never manually remove it from gitignore.**

---

## 3. Sharing as a Template
If you share this repository with someone who doesn't have an API key configured:

-   The application will start gracefully but will be "locked."
-   A **🗝️ Configuration** section will appear in the sidebar.
-   The user can enter their own API key, which will persist in their browser session for both the Chat and History Dashboard.

---

## 🛠️ Requirements
-   **Python 3.9+**
-   **OpenAI API Key** (with GPT-4o and GPT-4o-mini access)
-   **SQLite** (Built-in to Python)

---

> [!TIP]
> **Budget Tracking**: Even when using the UI Input, the application still calculates the estimated **GPT-5.1 cost** and tracks token usage in the History Dashboard for full financial transparency.
