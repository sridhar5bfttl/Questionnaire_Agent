import streamlit as st
import pandas as pd
from app.utils.db_manager import (
    get_admin_user_stats, 
    get_all_quota_requests, 
    update_quota_request, 
    get_system_settings, 
    update_system_setting,
    set_user_quota,
    get_pending_users,
    update_user_status
)
from app.config import ADMIN_USER, ADMIN_PASS
import plotly.express as px

st.set_page_config(page_title="Vantage Point Admin", page_icon="🛡️", layout="wide")

from app.components.navigation import sidebar_nav
sidebar_nav()

# --- AUTHENTICATION ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.title("🛡️ Admin Secure Login")
    with st.form("login_form"):
        user = st.text_input("Admin Username")
        pw = st.text_input("Password", type="password")
        if st.form_submit_button("Access Dashboard"):
            if user == ADMIN_USER and pw == ADMIN_PASS:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
    st.stop()

# --- DASHBOARD UI ---
st.title("🛡️ Strategic Admin Command Center")
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"admin_logged_in": False}))

settings = get_system_settings()
admin_email = settings.get('admin_notification_email', 'admin@vantagepoint.ai')

# --- TABBED INTERFACE ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 User Activity Stats", "📬 Quota Requests", "📝 New Registrations", "⚙️ System Settings"])

with tab1:
    st.header("Global User Intelligence")
    stats = get_admin_user_stats()
    if stats:
        df = pd.DataFrame(stats)
        
        # Prettify the dataframe for display
        display_df = df.reindex(columns=[
            'user_id', 'status', 'signup_date', 'last_decision_date', 
            'max_sessions', 'total_sessions', 'remaining_quota', 
            'last_active', 'avg_audit_score'
        ])
        
        display_df.columns = [
            'User Email', 'Account Status', 'Joined Date', 'Approved Date',
            'Total Quota', 'Sessions Used', 'Remaining', 
            'Last Active', 'Avg Audit Score'
        ]
        
        st.dataframe(display_df.sort_values('Last Active', ascending=False), width=1500)
        
        # Simple Viz
        fig = px.scatter(df, x="total_sessions", y="avg_audit_score", 
                         size="total_input", color="status", hover_name="user_id",
                         title="Engagement vs. Quality Matrix")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No user activity recorded yet.")

with tab2:
    st.header("Pending & Historical Requests")
    requests = get_all_quota_requests()
    if requests:
        for req in requests:
            with st.expander(f"Request {req['id']}: {req['user_id']} ({req['status']})", expanded=(req['status'] == 'PENDING')):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**Requested At:** {req['requested_at']}")
                    st.write(f"**Request Type:** {req.get('request_type', 'EXTENSION')}")
                    st.write(f"**Desired Session Limit:** {req.get('requested_limit', 10)}")
                    st.write(f"**Justification:**")
                    st.info(req['justification'])
                
                with c2:
                    if req['status'] == 'PENDING':
                        new_notes = st.text_area("Admin Notes", key=f"notes_{req['id']}")
                        # New Limit Controls - pre-fill with requested value
                        suggested_limit = req.get('requested_limit', 20)
                        new_limit = st.number_input("Grant Session Limit", min_value=10, max_value=200, value=max(10, suggested_limit), key=f"limit_{req['id']}")
                        new_daily = st.number_input("Grant Daily Limit", min_value=2, max_value=50, value=5, key=f"daily_{req['id']}")
                        
                        col_a, col_r = st.columns(2)
                        if col_a.button("Approve", key=f"app_{req['id']}"):
                            update_quota_request(req['id'], 'APPROVED', new_notes)
                            set_user_quota(req['user_id'], new_limit, new_daily)
                            if req.get('request_type') == 'SIGNUP':
                                update_user_status(req['user_id'], 'APPROVED')
                            st.success("Approved!")
                            st.rerun()
                        if col_r.button("Reject", key=f"rej_{req['id']}", type="primary"):
                            update_quota_request(req['id'], 'REJECTED', new_notes)
                            st.error("Rejected.")
                            st.rerun()
                    else:
                        st.write(f"**Decision at:** {req['decision_at']}")
                        st.write(f"**Notes:** {req['admin_notes']}")
    else:
        st.info("No extension requests received.")

with tab3:
    st.header("New Account Approvals")
    pending = get_pending_users()
    if pending:
        for p in pending:
            with st.container():
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"**Email:** {p['user_id']}")
                c1.caption(f"Joined: {p['created_at']}")
                if c2.button("✅ Approve", key=f"app_user_{p['user_id']}"):
                    update_user_status(p['user_id'], 'APPROVED')
                    st.success(f"Approved {p['user_id']}")
                    st.rerun()
                if c3.button("❌ Reject", key=f"rej_user_{p['user_id']}", type="primary"):
                    update_user_status(p['user_id'], 'REJECTED')
                    st.error(f"Rejected {p['user_id']}")
                    st.rerun()
                st.divider()
    else:
        st.info("No pending registrations at the moment.")

with tab4:
    st.header("Global Constants")
    new_email = st.text_input("Admin Notification Email", value=admin_email)
    new_threshold = st.slider("Audit Score Threshold (Weak vs Healthy)", 0, 10, int(settings.get('audit_threshold', 4)))
    
    if st.button("Save Settings"):
        update_system_setting('admin_notification_email', new_email)
        update_system_setting('audit_threshold', str(new_threshold))
        st.success("Settings updated globally.")
