import streamlit as st
import os

def render_starter_prompts():
    """Render the 5 starter prompts as buttons."""
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "greeting_prompts.txt")
    
    if not os.path.exists(prompt_path):
        st.error("Starter prompts file not found.")
        return None

    with open(prompt_path, "r") as f:
        prompts = [line.strip() for line in f.readlines() if line.strip()]

    st.write("### Choose a starter prompt or describe your use case:")
    
    # Render prompts in columns or a list of buttons
    selected_prompt = None
    for prompt in prompts:
        if st.button(prompt, width="stretch"):
            selected_prompt = prompt
            
    return selected_prompt
