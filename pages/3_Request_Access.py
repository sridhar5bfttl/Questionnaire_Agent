import streamlit as st
from app.utils.db_manager import (
    create_quota_request, 
    get_user_status, 
    get_user_stats, 
    get_all_quota_requests
)
from app.utils.quota_agent import QuotaAgent

st.set_page_config(page_title="Vantage Point AI - Access Portal", page_icon="🚀", layout="centered")

st.title("🚀 Strategic Access & Quota Portal")
st.markdown("""
Welcome to the Vantage Point AI Access Center. Use this form to either **request a new account approval** 
or to **request a quota extension** for your existing technical strategy sessions.
""")

# Detect current context
is_logged_in = not st.session_state.get("is_guest", True)
current_user = st.session_state.get("user_id", "guest_default")

# If coming from a failed login or quota block
target_email = st.session_state.get("request_email", "" if current_user == "guest_default" else current_user)

# Status Check Logic
if target_email:
    status = get_user_status(target_email)
    all_reqs = get_all_quota_requests()
    pending = [r for r in all_reqs if r['user_id'] == target_email and r['status'] == 'PENDING']
    
    if status == "APPROVED" and not is_logged_in:
        st.success(f"✅ **Account Approved**: {target_email} is already registered. Please go back and login.")
        if st.button("Back to Login"): st.switch_page("app.py")
        st.stop()
    elif pending:
        st.warning(f"⏳ **Status: Pending Review**")
        st.info(f"Your {pending[0]['request_type']} request for **{target_email}** is currently being reviewed by an administrator. You will be able to access the platform once your account is activated.")
        if st.button("Back to App"): st.switch_page("app.py")
        st.stop()

with st.form("request_form"):
    st.subheader("📋 Request Details")
    
    email = st.text_input("Email Address", value=target_email, 
                          help="Use the email address you want registered or the one you are currently using.")
    
    req_type = "EXTENSION" if is_logged_in else "SIGNUP"
    if not is_logged_in:
        req_type = st.radio("Request Type", ["SIGNUP", "EXTENSION"], 
                           index=0, horizontal=True,
                           help="Choose SIGNUP if this is your first time. Choose EXTENSION if you hit a quota limit.")
    else:
        st.info(f"📍 logged in as {current_user} - Requesting Quota Extension")

    use_case = st.text_area("Use Case Description", 
                           placeholder="Describe the technical strategy problem you are solving (e.g., 'Mapping RPA workflows for finance department').",
                           help="Our AI agent will review this to draft a justification for the admin.")
    
    req_quota = st.number_input("Requested Sessions", min_value=10, max_value=100, value=20, step=5)
    
    submit = st.form_submit_button("🚀 Submit Request to Administrator")

if submit:
    if not email or "@" not in email:
        st.error("Please enter a valid email address.")
    elif not use_case or len(use_case) < 30:
        st.error("Please provide a more detailed use case description (min 30 characters).")
    else:
        with st.spinner("Analyzing request and notifying administrator..."):
            # Check for existing pending request
            all_reqs = get_all_quota_requests()
            pending = [r for r in all_reqs if r['user_id'] == email and r['status'] == 'PENDING']
            
            if pending:
                st.warning(f"⏳ You already have a pending {pending[0]['request_type']} request. Please wait for review.")
            else:
                # Use Agent to enhance justification if possible, else use provided text
                stats = get_user_stats(email)
                qa = QuotaAgent()
                # Simulate agent enhancement
                enhanced_justification = f"USER INPUT: {use_case}\n\n"
                try:
                    agent_words = qa.generate_justification(email, st.session_state.get('messages', []), stats)
                    enhanced_justification += f"AGENT ANALYSIS: {agent_words}"
                except:
                    enhanced_justification += "Agent analysis unavailable."

                create_quota_request(
                    email, 
                    is_guest=(not is_logged_in), 
                    justification=enhanced_justification,
                    request_type=req_type,
                    requested_limit=req_quota
                )
                
                st.success("✅ **Success!** Your request has been transmitted. The administrator will review your use case and notify you.")
                st.balloons()
                
                # Optional: clear state
                if "request_email" in st.session_state:
                    del st.session_state.request_email

st.divider()
st.markdown("### ❓ Frequently Asked Questions")
with st.expander("How long does approval take?"):
    st.write("Requests are usually reviewed within 1-2 business hours by our technical strategy leads.")

with st.expander("Why was my request denied?"):
    st.write("Requests are typically denied if the use case description is too vague or doesn't align with strategic architecture mapping (RPA/ML/GenAI).")

if st.button("⬅️ Back to Main App"):
    st.switch_page("app.py")
