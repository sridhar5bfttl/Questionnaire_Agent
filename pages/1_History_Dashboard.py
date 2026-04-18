import streamlit as st
import os
import pandas as pd
import plotly.express as px
from app.utils.state import init_state
from app.utils.db_manager import get_all_sessions, get_session_messages, get_session_assessment, hide_session, get_session_duration, search_sessions, update_session_title
from app.utils.pdf_generator import generate_assessment_pdf

init_state()

st.set_page_config(page_title="History Dashboard", page_icon="📜", layout="wide")

# Custom CSS Injection
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    load_css("assets/custom_styles.css")
except:
    pass

st.title("🎯 Vantage Point AI: History")
st.markdown("Review previous assessments, token usage, and AI audit scores.")

# --- API KEY GUARD ---
existing_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not existing_key and "openai_api_key" not in st.session_state:
    st.warning("Please provide an OpenAI API key in the main chat sidebar to access history features.")
    st.stop()

# Fetch all sessions
sessions = get_all_sessions(user_id=st.session_state.user_id)

if not sessions:
    st.info("No saved conversations found. Start a chat and save it to see it here!")
else:
    # Sidebar Session Selector
    st.sidebar.header("Session Navigator")

    # --- KEYWORD SEARCH ---
    search_query = st.sidebar.text_input(
        "🔍 Search Sessions",
        placeholder="e.g. RPA, invoice, GenAI...",
        help="Search across session titles, messages, and audit feedback."
    )

    if search_query.strip():
        matched_sessions = search_sessions(search_query.strip(), user_id=st.session_state.user_id)
        if not matched_sessions:
            st.sidebar.warning(f"No sessions found for '{search_query}'.")
            display_sessions = []
        else:
            st.sidebar.success(f"Found {len(matched_sessions)} matching session(s)")
            display_sessions = matched_sessions
    else:
        display_sessions = sessions
        matched_sessions = []

    if not display_sessions:
        st.info("No sessions match your search. Try a different keyword.")
        st.stop()

    # Format session list for display - show title + formatted date
    session_options = {
        f"{s['title']} — {s['timestamp'][:10]}": s['id']
        for s in display_sessions
    }
    selected_label = st.sidebar.radio("View Details For:", list(session_options.keys()))
    selected_session_id = session_options[selected_label]

    # Show match snippet if in search mode
    if search_query.strip():
        selected_match = next((s for s in display_sessions if s['id'] == selected_session_id), None)
        if selected_match and selected_match.get("match_snippet"):
            st.sidebar.caption(f"💡 **Match**: {selected_match['match_snippet'][:100]}...")

    # --- RENAME FEATURE ---
    current_session = next((s for s in display_sessions if s['id'] == selected_session_id), None)
    with st.sidebar.expander("✏️ Rename Session"):
        new_title = st.text_input("New Title", value=current_session['title'] if current_session else "")
        if st.button("Save Title", width="stretch"):
            if new_title.strip():
                update_session_title(selected_session_id, new_title.strip())
                st.toast("Title updated!")
                st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("🗑️ Hide from List", width="stretch"):
        hide_session(selected_session_id)
        st.toast(f"Session '{selected_label}' hidden!")
        st.rerun()

    if st.sidebar.button("🚀 Resume Conversation", width="stretch", type="primary"):
        st.session_state.resume_session_id = selected_session_id
        st.switch_page("app.py")

    # Main Metrics & Visualization Dashboard
    st.subheader("📊 Global Analytics")
    
    # Calculate global metrics
    df_sessions = pd.DataFrame(sessions)
    
    # Filter for active sessions in numeric calc
    active_df = df_sessions[df_sessions['is_active'] == 1].copy()
    
    # 1. Visualization Row
    vcol1, vcol2 = st.columns([1, 1])
    
    with vcol1:
        # Token Usage Timeline (Bar Chart)
        fig_tokens = px.bar(
            active_df, 
            x='timestamp', 
            y=['input_tokens', 'output_tokens'],
            title="Token Consumption Timeline",
            labels={'value': 'Tokens', 'timestamp': 'Session Date'},
            barmode='group',
            color_discrete_sequence=['#007BFF', '#00D4FF']
        )
        fig_tokens.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_tokens, use_container_width=True) # Plotly still uses this kwarg

    with vcol2:
        # Cost Trend (Area Chart)
        active_df = active_df.sort_values('timestamp')
        active_df['cumulative_cost'] = active_df['total_cost'].cumsum()
        fig_cost = px.area(
            active_df, 
            x='timestamp', 
            y='cumulative_cost',
            title="Cumulative Budget Utilization (GPT-5.1)",
            labels={'cumulative_cost': 'Total Cost ($)', 'timestamp': 'Date'},
            color_discrete_sequence=['#28A745']
        )
        fig_cost.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_cost, use_container_width=True) # Plotly still uses this kwarg

    st.divider()

    # Detailed Session View
    selected_session = next(s for s in sessions if s['id'] == selected_session_id)
    
    # Pre-fetch all data for the common download button
    messages_history = get_session_messages(selected_session_id)
    assessment = get_session_assessment(selected_session_id)
    
    # Section Header, Timestamps & Global Download
    duration_data = get_session_duration(selected_session_id)
    scol1, scol2 = st.columns([3, 1])
    with scol1:
        st.header(f"Topic: {selected_session['title']}")
        # Timestamp & Duration metrics row
        m1, m2, m3 = st.columns(3)
        m1.metric("📅 Started At", duration_data["started_at"])
        m2.metric("🏁 Last Message", duration_data["ended_at"])
        m3.metric("⏱️ Duration", duration_data["duration_formatted"])
    with scol2:
        if assessment:
            usage_data = {
                'input_tokens': selected_session['input_tokens'],
                'output_tokens': selected_session['output_tokens'],
                'total_cost': selected_session['total_cost']
            }
            pdf_bytes = generate_assessment_pdf(
                selected_session['title'], 
                assessment, 
                selected_session['audit_score'],
                selected_session['audit_feedback'],
                messages_history,
                usage_data
            )
            st.download_button(
                label="📄 Download Full Report",
                data=bytes(pdf_bytes),
                file_name=f"VantagePointReport_{selected_session['id']}.pdf",
                mime="application/pdf",
                width="stretch"
            )

    tab1, tab2, tab3 = st.tabs(["Conversation Transcript", "Technical Recommendation", "Audit Details"])

    with tab1:
        messages = get_session_messages(selected_session_id)
        if not messages:
            st.info("No messages found for this session.")
        else:
            # Show conversation directly as a trail with "Session X" markers
            last_burst = None
            for msg in messages:
                current_burst = msg.get("burst_number", 1)
                if current_burst != last_burst:
                    st.markdown(f"#### 🕓 Session {current_burst}")
                    last_burst = current_burst

                with st.chat_message(msg['role']):
                    st.markdown(msg['content'])
                    ts = msg.get("timestamp", "")
                    if ts:
                        label = "You" if msg["role"] == "user" else "Vantage Point AI"
                        st.caption(f"🕐 {label} · {ts}")

    with tab2:
        assessment = get_session_assessment(selected_session_id)
        if assessment:
            st.subheader(f"Classification: {assessment['classification']}")
            st.progress(assessment['confidence_score'] / 100, text=f"Confidence: {assessment['confidence_score']}%")
            st.markdown("### Rationale")
            st.info(assessment['rationale'])
        else:
            st.warning("No technical assessment was recorded for this session.")

    with tab3:
        st.subheader("AI Auditor Feedback")
        c1, c2 = st.columns([1, 3])
        with c1:
            st.metric("Audit Score", f"{selected_session['audit_score']}/10")
        with c2:
            st.markdown(f"**Feedback:** {selected_session['audit_feedback']}")
        
        st.divider()
        st.subheader("Resource Usage")
        st.write(f"**Input Tokens:** {selected_session['input_tokens']}")
        st.write(f"**Output Tokens:** {selected_session['output_tokens']}")
        st.write(f"**Cost Est. (GPT-5.1):** ${selected_session['total_cost']:.6f}")
