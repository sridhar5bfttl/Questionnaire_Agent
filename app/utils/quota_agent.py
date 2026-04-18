import streamlit as st
from .llm_client import LLMClient

class QuotaAgent:
    def __init__(self):
        self.llm = LLMClient()

    def generate_justification(self, user_email, conversation_history, usage_stats):
        """Generates a professional quota extension request based on user behavior."""
        history_str = "\n".join([f"{m['role']}: {m['content'][:100]}..." for m in conversation_history[-5:]])
        
        prompt = f"""
        You are a Quota Management Agent for Vantage Point AI.
        A user has exceeded their guest limits and is requesting an extension.
        
        USER EMAIL: {user_email}
        RECENT INTERACTION:
        {history_str}
        
        USAGE STATS:
        - Total Sessions: {usage_stats['total']}
        - Daily Sessions: {usage_stats['daily']}
        
        TASK: Write a 2-3 sentence professional justification to the administrator requesting a quota extension. 
        Focus on whether their use case seems legitimate based on the interaction above.
        If they seem to be testing seriously, justify the extension.
        """
        
        response = self.llm.generate_response(prompt)
        return response
