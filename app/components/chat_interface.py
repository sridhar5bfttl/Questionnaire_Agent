import streamlit as st

def render_chat_history(messages):
    """Render the chat history with collapsible session segments."""
    if not messages:
        return
        
    bursts = {}
    for m in messages:
        b = m.get("burst_number", 1)
        if b not in bursts: bursts[b] = []
        bursts[b].append(m)
        
    sorted_bursts = sorted(bursts.keys())
    for b_num in sorted_bursts:
        # Only expand the latest burst (or all if we want, but usually only latest)
        # Note: If we are in the middle of a chat, the latest burst is the current one.
        is_expanded = (b_num == sorted_bursts[-1])
        with st.expander(f"🕓 Session {b_num} Transcript", expanded=is_expanded):
            for message in bursts[b_num]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    ts = message.get("timestamp", "")
                    if ts:
                        label = "You" if message["role"] == "user" else "Vantage Point AI"
                        st.caption(f"🕐 {label} · {ts}")

def render_chat_input():
    """Render the chat input field and return the user input."""
    return st.chat_input("Describe your use case...")
