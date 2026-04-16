import pytest
from unittest.mock import MagicMock, patch
from app.utils.llm_client import LLMClient

@patch('app.utils.llm_client.ChatOpenAI')
def test_llm_client_initialization(mock_chat_openai):
    """Test that LLMClient initializes correctly with API key."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        client = LLMClient()
        assert client.client is not None

def test_llm_client_mock_response():
    """Test that LLMClient returns a mock response when no API key is present."""
    with patch.dict('os.environ', {}, clear=True):
        client = LLMClient()
        response = client.get_response([], "GREETING")
        assert "[MOCK]" in response

@patch('app.utils.llm_client.ChatOpenAI')
def test_llm_client_get_response(mock_chat_openai):
    """Test that get_response calls the internal client correctly."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        # Mock the invoke method
        mock_instance = MagicMock()
        mock_instance.invoke.return_value.content = "Assessment Complete"
        mock_chat_openai.return_value = mock_instance
        
        client = LLMClient()
        response = client.get_response([{"role": "user", "content": "test"}], "PROBING")
        
        assert response == "Assessment Complete"
        assert mock_instance.invoke.called
