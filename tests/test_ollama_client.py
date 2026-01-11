"""
Unit tests for Ollama client.

Tests async client functionality, error handling, and integration
with local Ollama server.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.data import (
    OllamaClient,
    ConnectionError,
    ModelNotFoundError,
    GenerationError,
    generate,
)


class TestOllamaClient:
    """Test suite for OllamaClient."""
    
    def test_init_default(self):
        """Test client initialization with defaults."""
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"
        assert client.timeout.total == 300
        
    def test_init_custom(self):
        """Test client initialization with custom values."""
        client = OllamaClient(
            base_url="http://custom:8080",
            timeout=60
        )
        assert client.base_url == "http://custom:8080"
        assert client.timeout.total == 60
        
    def test_base_url_stripping(self):
        """Test that trailing slashes are removed from base_url."""
        client = OllamaClient(base_url="http://localhost:11434/")
        assert client.base_url == "http://localhost:11434"
        
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager protocol."""
        async with OllamaClient() as client:
            assert client._session is not None
            assert not client._session.closed
            
        # Session should be closed after exiting context
        assert client._session is None or client._session.closed
        
    @pytest.mark.asyncio
    async def test_close(self):
        """Test explicit close method."""
        client = OllamaClient()
        await client._ensure_session()
        assert client._session is not None
        
        await client.close()
        assert client._session is None or client._session.closed


@pytest.mark.asyncio
class TestGeneration:
    """Tests for text generation."""
    
    async def test_generate_success(self):
        """Test successful generation."""
        client = OllamaClient()
        
        # Mock the session
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "model": "test-model",
            "response": "Test response",
            "done": True,
            "total_duration": 1000000,
            "eval_count": 10,
        })
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        client._session = mock_session
        
        # Test generation
        result = await client.generate(
            model="test-model",
            prompt="Test prompt"
        )
        
        assert result.model == "test-model"
        assert result.response == "Test response"
        assert result.done is True
        assert result.eval_count == 10
        
        await client.close()
        
    async def test_generate_with_system_prompt(self):
        """Test generation with system prompt."""
        client = OllamaClient()
        
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "model": "test-model",
            "response": "Response with system context",
            "done": True,
        })
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        client._session = mock_session
        
        result = await client.generate(
            model="test-model",
            prompt="User prompt",
            system="You are a helpful assistant."
        )
        
        assert result.response == "Response with system context"
        
        # Verify system prompt was included in request
        call_args = mock_session.post.call_args
        payload = call_args[1]["json"]
        assert payload["system"] == "You are a helpful assistant."
        
        await client.close()
        
    async def test_generate_model_not_found(self):
        """Test generation with non-existent model."""
        client = OllamaClient()
        
        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value="Model not found")
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        client._session = mock_session
        
        with pytest.raises(ModelNotFoundError) as exc_info:
            await client.generate(
                model="nonexistent-model",
                prompt="Test"
            )
            
        assert "nonexistent-model" in str(exc_info.value)
        
        await client.close()
        
    async def test_generate_server_error(self):
        """Test generation with server error."""
        client = OllamaClient()
        
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal server error")
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        client._session = mock_session
        
        with pytest.raises(GenerationError) as exc_info:
            await client.generate(model="test-model", prompt="Test")
            
        assert "500" in str(exc_info.value)
        
        await client.close()
        
    async def test_generate_connection_error(self):
        """Test generation with connection failure."""
        import aiohttp
        
        client = OllamaClient()
        
        mock_session = AsyncMock()
        mock_session.post.side_effect = aiohttp.ClientConnectorError(
            connection_key=MagicMock(),
            os_error=OSError("Connection refused")
        )
        client._session = mock_session
        
        with pytest.raises(ConnectionError) as exc_info:
            await client.generate(model="test-model", prompt="Test")
            
        assert "Cannot connect" in str(exc_info.value)
        
        await client.close()


@pytest.mark.asyncio
class TestModelManagement:
    """Tests for model listing and management."""
    
    async def test_list_models(self):
        """Test listing available models."""
        client = OllamaClient()
        
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "models": [
                {
                    "name": "llama3.2:3b",
                    "size": 2000000000,
                    "modified_at": "2026-01-11T00:00:00Z",
                    "digest": "abc123"
                },
                {
                    "name": "qwen2.5-coder:7b",
                    "size": 4700000000,
                    "modified_at": "2026-01-11T00:00:00Z",
                    "digest": "def456"
                }
            ]
        })
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        client._session = mock_session
        
        models = await client.list_models()
        
        assert len(models) == 2
        assert models[0].name == "llama3.2:3b"
        assert models[0].size == 2000000000
        assert models[1].name == "qwen2.5-coder:7b"
        
        await client.close()
        
    async def test_check_health_success(self):
        """Test health check with running server."""
        client = OllamaClient()
        
        mock_response = MagicMock()
        mock_response.status = 200
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        client._session = mock_session
        
        healthy = await client.check_health()
        
        assert healthy is True
        
        await client.close()
        
    async def test_check_health_failure(self):
        """Test health check with non-responsive server."""
        import aiohttp
        
        client = OllamaClient()
        
        mock_session = AsyncMock()
        mock_session.get.side_effect = aiohttp.ClientConnectorError(
            connection_key=MagicMock(),
            os_error=OSError("Connection refused")
        )
        client._session = mock_session
        
        healthy = await client.check_health()
        
        assert healthy is False
        
        await client.close()
        
    async def test_model_exists_true(self):
        """Test checking for existing model."""
        client = OllamaClient()
        
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "models": [
                {
                    "name": "llama3.2:3b",
                    "size": 2000000000,
                    "modified_at": "2026-01-11T00:00:00Z",
                    "digest": "abc123"
                }
            ]
        })
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        client._session = mock_session
        
        exists = await client.model_exists("llama3.2:3b")
        
        assert exists is True
        
        await client.close()
        
    async def test_model_exists_false(self):
        """Test checking for non-existent model."""
        client = OllamaClient()
        
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"models": []})
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        client._session = mock_session
        
        exists = await client.model_exists("nonexistent-model")
        
        assert exists is False
        
        await client.close()


@pytest.mark.asyncio
class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    async def test_generate_function(self):
        """Test convenience generate function."""
        with patch('src.data.ollama_client.OllamaClient') as MockClient:
            mock_client_instance = AsyncMock()
            mock_client_instance.generate = AsyncMock(return_value=MagicMock(
                response="Test response"
            ))
            MockClient.return_value.__aenter__.return_value = mock_client_instance
            
            response = await generate(
                model="test-model",
                prompt="Test prompt"
            )
            
            assert response == "Test response"


# Integration tests (require running Ollama server)
@pytest.mark.integration
@pytest.mark.asyncio
class TestIntegration:
    """Integration tests with real Ollama server."""
    
    async def test_real_connection(self):
        """Test connection to real Ollama server."""
        async with OllamaClient() as client:
            healthy = await client.check_health()
            
            # Skip if Ollama not running
            if not healthy:
                pytest.skip("Ollama server not running")
                
            # List models
            models = await client.list_models()
            assert len(models) > 0
            
    async def test_real_generation(self):
        """Test real generation with Ollama."""
        async with OllamaClient() as client:
            healthy = await client.check_health()
            
            if not healthy:
                pytest.skip("Ollama server not running")
                
            # Get first available model
            models = await client.list_models()
            if not models:
                pytest.skip("No models available")
                
            test_model = models[0].name
            
            # Generate response
            response = await client.generate(
                model=test_model,
                prompt="Say hello in one word.",
                temperature=0.1  # Low temp for deterministic output
            )
            
            assert response.response
            assert response.done is True
            assert response.eval_count > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
