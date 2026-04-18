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
    """Test that LLMClient returns a dict with MOCK content when no API key is present."""
    with patch.dict('os.environ', {}, clear=True):
        client = LLMClient()
        response = client.get_response([], "GREETING")
        # get_response always returns a dict with 'content' and 'metadata' keys
        assert isinstance(response, dict)
        assert "content" in response
        assert "[MOCK]" in response["content"]

@patch('app.utils.llm_client.ChatOpenAI')
def test_llm_client_get_response(mock_chat_openai):
    """Test that get_response calls the internal client and returns a dict."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        mock_instance = MagicMock()
        mock_instance.invoke.return_value.content = "Assessment Complete"
        mock_instance.invoke.return_value.response_metadata = {"token_usage": {"prompt_tokens": 10, "completion_tokens": 20}}
        mock_chat_openai.return_value = mock_instance

        client = LLMClient()
        response = client.get_response([{"role": "user", "content": "test"}], "PROBING")

        assert isinstance(response, dict)
        assert response["content"] == "Assessment Complete"
        assert mock_instance.invoke.called

def test_llm_client_no_key_returns_mock_not_none():
    """Test that the mock client gracefully responds with a non-empty string."""
    with patch.dict('os.environ', {}, clear=True):
        client = LLMClient()
        assert client.client is None
        response = client.get_response([], "PROBING")
        assert response["content"] is not None
        assert len(response["content"]) > 0
