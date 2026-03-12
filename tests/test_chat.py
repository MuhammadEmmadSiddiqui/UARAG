"""Tests for chat endpoints."""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_chat_history_empty(auth_client: AsyncClient):
    """Test getting empty chat history."""
    response = await auth_client.get("/chat/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_chat_stream_unauthorized(test_client: AsyncClient):
    """Test chat streaming without authentication."""
    response = await test_client.post(
        "/chat/stream",
        json={"message": "Hello"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_stream_empty_message(auth_client: AsyncClient):
    """Test chat streaming with empty message."""
    response = await auth_client.post(
        "/chat/stream",
        json={"message": ""}
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
@patch('backend.chat.get_llm')
async def test_chat_stream_success(mock_get_llm, auth_client: AsyncClient):
    """Test successful chat streaming."""
    # Mock LLM response
    class MockChunk:
        def __init__(self, content):
            self.content = content
    
    async def mock_astream(*args, **kwargs):
        chunks = ["Hello", " ", "World", "!"]
        for chunk in chunks:
            yield MockChunk(chunk)
    
    mock_llm = AsyncMock()
    mock_llm.astream = mock_astream
    mock_chain = AsyncMock()
    mock_chain.astream = mock_astream
    
    # Create a mock that supports the | operator
    class MockLLM:
        def __init__(self):
            pass
        
        async def astream(self, *args, **kwargs):
            async for chunk in mock_astream():
                yield chunk
    
    mock_get_llm.return_value = MockLLM()
    
    response = await auth_client.post(
        "/chat/stream",
        json={"message": "Hello"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/x-ndjson"


@pytest.mark.asyncio
async def test_get_nonexistent_conversation(auth_client: AsyncClient):
    """Test getting nonexistent conversation."""
    response = await auth_client.get("/chat/conversation/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_health_check(test_client: AsyncClient):
    """Test health check endpoint."""
    response = await test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint(test_client: AsyncClient):
    """Test root endpoint."""
    response = await test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_chat_request_validation(auth_client: AsyncClient):
    """Test chat request validation."""
    # Missing message field
    response = await auth_client.post(
        "/chat/stream",
        json={}
    )
    assert response.status_code == 422
    
    # Invalid conversation_id type
    response = await auth_client.post(
        "/chat/stream",
        json={"message": "Hello", "conversation_id": "invalid"}
    )
    assert response.status_code == 422
