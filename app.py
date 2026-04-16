import streamlit as st
from app.utils.state import init_state, ChatPhase, update_phase, add_message, get_messages
from app.utils.llm_client import LLMClient
from app.components.chat_interface import render_chat_history, render_chat_input
from app.components.starter_prompts import render_starter_prompts

# Page Configuration
st.set_page_config(page_title="Questionnaire Agent", page_icon="🤖", layout="wide")

# Initialize Session State
init_state()

# Title and Description
st.title("🤖 Use Case Assessment Agent")
st.markdown("""
Welcome! I'm here to help you classify your business use case and determine the best technical solution—whether it's **RPA, ML, DL, NLP, or GenAI**.
""")

# Initialize LLM Client
llm = LLMClient()

# Render Chat History
render_chat_history(get_messages())

# --- USER INPUT HANDLING ---

# 1. Handling Starter Prompts (Greeting Phase Only)
if st.session_state.phase == ChatPhase.GREETING:
    selected_prompt = render_starter_prompts()
    if selected_prompt:
        add_message("user", selected_prompt)
        update_phase(ChatPhase.PROBING)
        st.rerun()

# 2. Handling Manual Chat Input
user_input = render_chat_input()
if user_input:
    add_message("user", user_input)
    if st.session_state.phase == ChatPhase.GREETING:
        update_phase(ChatPhase.PROBING)
    st.rerun()

# --- AI RESPONSE GENERATION ---
# Check if the last message is from the user; if so, trigger AI response
messages = get_messages()
if messages and messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = llm.get_response(messages, st.session_state.phase)
            
            # Detect Phase Changes
            if "[PHASE_CHANGE: SUMMARY]" in response:
                update_phase(ChatPhase.SUMMARY)
                response = response.replace("[PHASE_CHANGE: SUMMARY]", "").strip()
            elif "[PHASE_CHANGE: DEEP_DIVE]" in response:
                update_phase(ChatPhase.DEEP_DIVE)
                response = response.replace("[PHASE_CHANGE: DEEP_DIVE]", "").strip()
            
            st.markdown(response)
            add_message("assistant", response)
            st.rerun()

# --- DYNAMIC UI UPDATES ---

# Feedback & Export UI
if st.session_state.phase in [ChatPhase.SUMMARY, ChatPhase.FEEDBACK]:
    st.divider()
    cols = st.columns([1, 1, 2])
    with cols[0]:
        if st.button("📧 Export to Email"):
            st.success("Summary ready for export! (mailto: link would open here)")
            if st.session_state.phase != ChatPhase.FEEDBACK:
                update_phase(ChatPhase.FEEDBACK)
                st.rerun()
    with cols[1]:
        if st.button("🔍 Start Deep Dive"):
            update_phase(ChatPhase.DEEP_DIVE)
            add_message("user", "I want to do a deep dive into the selected solution.")
            st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"Current Phase: **{st.session_state.phase.name}**")
if st.sidebar.button("Reset Chat"):
    st.session_state.clear()
    st.rerun()
