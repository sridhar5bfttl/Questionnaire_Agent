import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

class LLMClient:
    def __init__(self, model_name="gpt-4o"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Placeholder/Mock if no API key is found for local dev
            self.client = None
        else:
            self.client = ChatOpenAI(model=model_name, api_key=api_key)

    def _get_system_prompt(self):
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "system_prompt.txt")
        with open(prompt_path, "r") as f:
            return f.read()

    def get_response(self, messages, current_phase):
        if not self.client:
            return {
                "content": f"[MOCK] This is a mock response for phase {current_phase}. Please set OPENAI_API_KEY.",
                "metadata": {"token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}
            }

        system_msg = SystemMessage(content=self._get_system_prompt())
        
        # Convert streamlit messages to LangChain messages
        langchain_msgs = [system_msg]
        for m in messages:
            content = m["content"]
            # Handle cases where content might be a dictionary from previous state bugs
            if isinstance(content, dict):
                content = content.get("content", str(content))
            
            if m["role"] == "user":
                langchain_msgs.append(HumanMessage(content=content))
            else:
                langchain_msgs.append(AIMessage(content=content))
        
        response = self.client.invoke(langchain_msgs)
        return {
            "content": response.content,
            "metadata": response.response_metadata.get("token_usage", {})
        }
