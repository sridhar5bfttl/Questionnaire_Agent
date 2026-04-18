import streamlit as st
import os
from app.utils.state import init_state, ChatPhase, update_phase, add_message, get_messages, load_session_state
from app.utils.llm_client import LLMClient
from app.components.chat_interface import render_chat_history, render_chat_input
from app.components.starter_prompts import render_starter_prompts
from app.utils.db_manager import (
    init_db, save_chat_session, save_assessment, 
    get_session_messages, get_all_sessions, get_user_stats,
    log_activity, create_quota_request, get_all_quota_requests,
    get_system_settings, get_user_quota, ensure_user, get_user_status
)
from app.utils.auditor_agent import AuditorAgent
from app.utils.quota_agent import QuotaAgent
from app.config import (
    GUEST_MAX_SESSIONS, GUEST_DAILY_SESSIONS, 
    GUEST_TOKEN_LIMIT, AUDIT_THRESHOLD
)

# Page Configuration
st.set_page_config(page_title="Vantage Point AI", page_icon="🎯", layout="wide")

# Initialize Session State, Database & Auditor
init_state()
init_db()

# --- RESUME LOGIC ---
if "resume_session_id" in st.session_state and st.session_state.resume_session_id is not None:
    session_id = st.session_state.resume_session_id
    historical_msgs = get_session_messages(session_id)
    
    # Get metadata for the session (we need tokens and phase)
    all_sessions = get_all_sessions()
    session_metadata = next((s for s in all_sessions if s['id'] == session_id), {})
    
    from app.utils.state import load_session_state
    load_session_state(session_id, historical_msgs, session_metadata)
    
    # Clear the trigger flag
    del st.session_state.resume_session_id
    st.toast(f"Resumed session: {session_metadata.get('title', 'Unknown')}")

auditor = AuditorAgent()

def trigger_auto_save():
    """Shared logic to audit and save a session if it has content."""
    if not st.session_state.session_saved and len(st.session_state.messages) > 0:
        with st.sidebar:
            with st.spinner("Auto-saving..."):
                # 1. Title
                if not st.session_state.get("current_title"):
                    title = auditor.generate_title(st.session_state.messages)
                    st.session_state.current_title = title
                else:
                    title = st.session_state.current_title
                
                # 2. Score
                score, feedback = auditor.score_conversation(st.session_state.messages)
                
                # 3. Recommendation
                summary_text = ""
                for msg in reversed(st.session_state.messages):
                    if msg["role"] == "assistant":
                        summary_text = msg["content"]
                        break
                classification, confidence, rationale = auditor.extract_recommendation(summary_text)

                # 4. Cost
                cost = auditor.calculate_cost(
                    st.session_state.total_input_tokens, 
                    st.session_state.total_output_tokens
                )
                
                # 5. Persist (Update existing if resumed, otherwise creates new)
                session_id = save_chat_session(
                    st.session_state.messages, 
                    title=title,
                    summary="Unified Audit Save (Update)",
                    input_tokens=st.session_state.total_input_tokens,
                    output_tokens=st.session_state.total_output_tokens,
                    total_cost=cost,
                    audit_score=score,
                    audit_feedback=feedback,
                    current_phase=st.session_state.phase.name,
                    session_id=st.session_state.current_session_id, # Reverted to update
                    user_id=st.session_state.user_id,
                    is_guest=int(st.session_state.is_guest)
                )
                save_assessment(session_id, classification, confidence, rationale)
                st.session_state.session_saved = True
                return True
    return False

# --- API KEY GUARD ---
# Check prioritized order: Secrets -> Env -> SessionState
existing_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

with st.sidebar:
    st.subheader("👤 Identity")
    if st.session_state.is_guest:
        stats = get_user_stats(st.session_state.user_id)
        st.info(f"**Guest Mode Active**\n\n📅 Daily: {stats['daily']}/{GUEST_DAILY_SESSIONS} sessions\n📚 Total: {stats['total']}/{GUEST_MAX_SESSIONS} sessions")
        st.caption("Login using the main screen to unlock full access.")
    else:
        st.success(f"Logged in as: **{st.session_state.user_id}**")
        
        # User Stats Dashboard
        stats = get_user_stats(st.session_state.user_id)
        
        # Format duration
        tot_sec = stats['total_duration_seconds']
        h, m = int(tot_sec // 3600), int((tot_sec % 3600) // 60)
        dur_str = f"{h}h {m}m" if h > 0 else f"{m}m"
        
        with st.expander("📊 My Usage Dashboard", expanded=True):
            c1, c2 = st.columns(2)
            c1.metric("Sessions", f"{stats['total']}/{stats['max_sessions']}")
            c2.metric("Active Time", dur_str)
            
            # Progress bar for tokens
            used_tokens = stats['total_input'] + stats['total_output']
            max_tokens = stats['max_tokens']
            progress = min(1.0, used_tokens / max_tokens)
            st.caption(f"Token Consumption: {used_tokens:,} / {max_tokens:,}")
            st.progress(progress)
            
            if st.button("Request More Quota"):
                st.switch_page("pages/3_Request_Access.py")
        
        if st.button("Logout"):
            trigger_auto_save()
            st.session_state.user_id = "guest_default"
            st.session_state.is_guest = True
            st.rerun()
    
    st.divider()
    if not existing_key:
        st.subheader("🗝️ Configuration")
        user_key = st.text_input("Enter OpenAI API Key", type="password", help="Required for template users if no .env or secrets are set.")
        if user_key:
            st.session_state.openai_api_key = user_key
            st.success("Key applied for this session!")
        else:
            st.warning("Please add your OpenAI API key to start the diagnostic.")
            st.stop()
    else:
        st.caption("✅ API Key active (System)")

# Custom CSS Injection
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    load_css("assets/custom_styles.css")
except:
    pass

# --- MAIN UI WRAPPER ---
if st.session_state.is_guest and not st.session_state.bypass_login:
    # --- LANDING PAGE FOR NON-LOGGED IN USERS ---
    st.title("🎯 Vantage Point AI")
    st.markdown("### Technical Strategy & Architecture Partner")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("""
            Welcome! I am your technical strategy partner. I help you navigate through complex business 
            requirements to identify the perfect technical architecture.
        """)
        
        st.subheader("🔓 Access the Strategic Suite")
        login_email = st.text_input("Enter your Email Address", placeholder="user@example.com")
        
        c1, c2 = st.columns(2)
        if c1.button("Strategic Login", type="primary"):
            if login_email:
                ensure_user(login_email)
                status = get_user_status(login_email)
                if status == "APPROVED":
                    st.session_state.user_id = login_email
                    st.session_state.is_guest = False
                    log_activity(login_email, "LOGIN")
                    st.success("Access Granted!")
                    st.rerun()
                else:
                    st.session_state.request_email = login_email
                    st.switch_page("pages/3_Request_Access.py")
            else:
                st.error("Please enter your email.")
        
        if c2.button("Continue as Guest (Limited)"):
             st.session_state.bypass_login = True
             st.rerun()

    with col2:
         # Use a placeholder or generated image
         st.image("https://img.freepik.com/free-vector/strategic-consulting-concept-illustration_114360-8964.jpg", use_container_width=True)

    st.stop() # Stop execution here for landing page

# --- APP PAGE (CHAT INTERFACE) ---
st.title("🎯 Vantage Point AI")

# Display Active Topic Title if Resumed
if st.session_state.get("current_title"):
    st.subheader(f"📂 Topic: {st.session_state.current_title}")
    st.divider()

# Initialize LLM Client
llm = LLMClient()

# Render Chat History
render_chat_history(get_messages())

# Visual marker for NEW burst if session was resumed
if st.session_state.current_session_id and st.session_state.current_burst_number > 1:
    # Only show if the LAST message in history isn't already from THIS burst
    messages = get_messages()
    if not messages or messages[-1].get("burst_number") < st.session_state.current_burst_number:
        st.markdown(f"#### 🕓 Session {st.session_state.current_burst_number} (Resumed)")

# --- QUOTA & LIMIT CHECKS (Guest Mode) ---
quota_blocked = False
if st.session_state.is_guest:
    stats = get_user_stats(st.session_state.user_id)
    user_quota = get_user_quota(st.session_state.user_id)
    
    # 1. Conversation Count Limits (Only check if starting a NEW session)
    if not st.session_state.current_session_id:
        limit_reached = False
        if stats['daily'] >= user_quota['max_daily_sessions']:
            st.error(f"🚫 **Daily Limit Reached**: You have used your {user_quota['max_daily_sessions']} daily guest sessions.")
            limit_reached = True
        elif stats['total'] >= user_quota['max_sessions']:
            st.error(f"🚫 **Total Limit Reached**: You have reached the maximum of {user_quota['max_sessions']} guest sessions.")
            limit_reached = True
        
        if limit_reached:
            quota_blocked = True
            st.warning("⚠️ **Capacity Reached**: Your current quota has been exhausted.")
            st.info("💡 To continue your strategic analysis, please visit our Access & Quota Portal to request an extension or register your account.")
            
            if st.button("🚀 Go to Access & Quota Portal"):
                st.session_state.request_email = st.session_state.user_id
                st.switch_page("pages/3_Request_Access.py")
    
    # 2. Token Limit Check
    total_tokens = st.session_state.total_input_tokens + st.session_state.total_output_tokens
    if total_tokens > 3000:
        st.warning("⚠️ **Token Limit Reached**: This guest session has exceeded 3,000 tokens. To continue this specific deep dive, please login.")
        quota_blocked = True

# --- USER INPUT HANDLING ---

# 1. Handling Starter Prompts (Greeting Phase & No Messages Only)
if st.session_state.phase == ChatPhase.GREETING and not st.session_state.messages:
    if not quota_blocked:
        selected_prompt = render_starter_prompts()
        if selected_prompt:
            add_message("user", selected_prompt)
            update_phase(ChatPhase.PROBING)
            st.rerun()
    else:
        st.info("💡 Login to unlock more conversations.")

# 2. Handling Manual Chat Input
if not quota_blocked:
    user_input = render_chat_input()
    if user_input:
        add_message("user", user_input)
        if st.session_state.phase == ChatPhase.GREETING:
            update_phase(ChatPhase.PROBING)
        st.rerun()
else:
    # Disable input visually if blocked
    st.chat_input("Quota limit reached. Please login...", disabled=True)

# --- AI RESPONSE GENERATION ---
# Check if the last message is from the user; if so, trigger AI response
messages = get_messages()
if messages and messages[-1]["role"] == "user" and not quota_blocked:
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_data = llm.get_response(messages, st.session_state.phase)
            response_text = response_data["content"]
            metadata = response_data["metadata"]
            
            # Update Tokens
            st.session_state.total_input_tokens += metadata.get("prompt_tokens", 0)
            st.session_state.total_output_tokens += metadata.get("completion_tokens", 0)
            
            # Detect Phase Changes
            if "[PHASE_CHANGE: SUMMARY]" in response_text:
                update_phase(ChatPhase.SUMMARY)
                response_text = response_text.replace("[PHASE_CHANGE: SUMMARY]", "").strip()
            elif "[PHASE_CHANGE: DEEP_DIVE]" in response_text:
                update_phase(ChatPhase.DEEP_DIVE)
                response_text = response_text.replace("[PHASE_CHANGE: DEEP_DIVE]", "").strip()
            
            st.markdown(response_text)
            add_message("assistant", response_text)
            st.rerun()

# --- DYNAMIC UI UPDATES ---

# Feedback & Export UI
if st.session_state.phase in [ChatPhase.SUMMARY, ChatPhase.FEEDBACK]:
    st.divider()
    cols = st.columns([1, 1, 2])
    with cols[0]:
        if st.button("💾 Save to Database (w/ Audit)"):
            with st.spinner("Auditing conversation..."):
                # 1. Auditor Agent: Title, Score, Feedback, and Tech Rec
                # 1. Title Generation (Only if not already titled)
                if not st.session_state.get("current_title"):
                    title = auditor.generate_title(st.session_state.messages)
                    st.session_state.current_title = title
                else:
                    title = st.session_state.current_title
                
                score, feedback = auditor.score_conversation(st.session_state.messages)
                
                # Find the summary text to extract recommendation from
                # Search for the last assistant message that triggered the summary phase
                summary_text = ""
                for msg in reversed(st.session_state.messages):
                    if msg["role"] == "assistant":
                        summary_text = msg["content"]
                        break
                
                classification, confidence, rationale = auditor.extract_recommendation(summary_text)
                
                # 2. Cost Calculation (GPT-5.1)
                cost = auditor.calculate_cost(
                    st.session_state.total_input_tokens, 
                    st.session_state.total_output_tokens
                )
                
                # 3. Save to DB (Update if Resumed, Otherwise New)
                session_id = save_chat_session(
                    st.session_state.messages, 
                    title=title,
                    summary="Manual Audit Save (Sync)",
                    input_tokens=st.session_state.total_input_tokens,
                    output_tokens=st.session_state.total_output_tokens,
                    total_cost=cost,
                    audit_score=score,
                    audit_feedback=feedback,
                    current_phase=st.session_state.phase.name,
                    session_id=st.session_state.current_session_id, # Reverted to update
                    user_id=st.session_state.user_id,
                    is_guest=int(st.session_state.is_guest)
                )
                st.session_state.current_session_id = session_id
                
                # 4. Save technical assessment
                save_assessment(session_id, classification, confidence, rationale)
                
                st.session_state.session_saved = True
                st.success(f"Assessment saved and audited! (Session ID: {session_id})")
                st.info(f"📌 **Title:** {title}\n\n🤖 **Rec:** {classification} ({confidence}%)\n\n📊 **Audit Score:** {score}/10 | 💰 **Est. Cost (GPT-5.1):** ${cost:.6f}")
                
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
    # Auto-save before reset if not already saved and history exists
    if trigger_auto_save():
        st.toast("Session auto-saved!")

    # Preserve identity state
    uid = st.session_state.user_id
    guest_flag = st.session_state.is_guest
    api_key = st.session_state.get("openai_api_key")
    
    st.session_state.clear()
    
    # Restore identity
    st.session_state.user_id = uid
    st.session_state.is_guest = guest_flag
    if api_key: st.session_state.openai_api_key = api_key
    
    st.rerun()
