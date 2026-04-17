import sys
import os
import streamlit as st
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.llm_client import LLMClient

def verify_tier3_auth():
    print("Testing 3-Tier Auth (Session State fallback)...")
    
    # Simulate missing env/secrets
    os.environ.pop("OPENAI_API_KEY", None)
    
    # Mock streamlit session state
    st.session_state["openai_api_key"] = "test_key_from_ui"
    
    try:
        client = LLMClient()
        # In our implementation, if a key is found, it initializes ChatOpenAI
        if client.client:
            print("SUCCESS: LLMClient detected key from session_state.")
        else:
            print("FAILURE: LLMClient did not detect key from session_state.")
            
    except Exception as e:
        print(f"FAILURE: Auth check failed with error: {e}")

if __name__ == "__main__":
    verify_tier3_auth()
