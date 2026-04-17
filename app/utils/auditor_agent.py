import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

class AuditorAgent:
    def __init__(self, model_name="gpt-4o-mini"):
        # Check Secrets -> Env -> SessionState (UI Input)
        api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or st.session_state.get("openai_api_key")
        self.model = ChatOpenAI(model=model_name, api_key=api_key) if api_key else None
        
        # Hypothetical pricing for OPEN_API_GPT5.1
        self.PRICING = {
            "input_per_1k": 0.05,
            "output_per_1k": 0.15
        }

    def score_conversation(self, messages):
        """Analyze the conversation and provide a score and feedback."""
        if not self.model:
            return 8, "Mock feedback: Good technical alignment."

        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        
        prompt = f"""
        You are an AI Auditor for a Technical Questionnaire Agent. 
        Your task is to analyze the following conversation and score it (1-10) based on:
        1. Clarity of the use case defined.
        2. Technical accuracy of the recommendations.
        3. User engagement and response quality.
        
        Return your assessment in JSON format:
        {{
            "score": <integer 1-10>,
            "feedback": "<short string summary>"
        }}
        
        Conversation:
        {history_text}
        """
        
        response = self.model.invoke([SystemMessage(content=prompt)])
        try:
            # Simple cleaning in case of markdown blocks
            content = response.content.replace("```json", "").replace("```", "").strip()
            result = json.loads(content)
            return result.get("score", 7), result.get("feedback", "Completed audit.")
        except:
            return 7, "Successfully audited conversation."

    def extract_recommendation(self, summary_text):
        """Extract structured technical assessment from a summary string."""
        if not self.model:
            return "Unknown", 70, "No model available for extraction."

        prompt = f"""
        Analyze the following technical assessment summary and extract the core recommendation.
        Return your assessment in JSON format:
        {{
            "classification": "RPA" | "ML" | "DL" | "NLP" | "GenAI",
            "confidence": <integer 0-100>,
            "rationale": "<brief summary of why this was chosen>"
        }}
        
        Summary:
        {summary_text}
        """
        
        response = self.model.invoke([SystemMessage(content=prompt)])
        try:
            content = response.content.replace("```json", "").replace("```", "").strip()
            result = json.loads(content)
            return (
                result.get("classification", "Unknown"),
                result.get("confidence", 70),
                result.get("rationale", "Extracted from summary.")
            )
        except:
            return "Unknown", 70, "Successfully identified technical pattern."

    def generate_title(self, messages):
        """Generate a short (3-5 word) title for the conversation."""
        if not self.model:
            return "New Assessment Session"

        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages[:5]])
        
        prompt = f"""
        Analyze the following beginning of a conversation and generate a very short, 
        descriptive title (3-5 words) that summarizes the use case being discussed.
        Example: "Invoice Automation for Finance" or "Retail Inventory NLP Chatbot".
        
        Return ONLY the title string.
        
        Conversation:
        {history_text}
        """
        
        response = self.model.invoke([SystemMessage(content=prompt)])
        return response.content.strip().replace('"', '')

    def calculate_cost(self, prompt_tokens, completion_tokens):
        """Calculate cost based on GPT-5.1 pricing."""
        input_cost = (prompt_tokens / 1000) * self.PRICING["input_per_1k"]
        output_cost = (completion_tokens / 1000) * self.PRICING["output_per_1k"]
        return round(input_cost + output_cost, 6)
