"""
Ollama Client Module for CardForge

Provides async interface to local Ollama server for AI agent execution.
Handles HTTP communication, streaming, health checks, and error management.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, AsyncIterator
from dataclasses import dataclass
from enum import Enum

import aiohttp


logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Base exception for Ollama client errors."""
    pass


class ConnectionError(OllamaError):
    """Raised when unable to connect to Ollama server."""
    pass


class ModelNotFoundError(OllamaError):
    """Raised when requested model is not available."""
    pass


class GenerationError(OllamaError):
    """Raised when generation fails."""
    pass


@dataclass
class GenerateResponse:
    """Response from Ollama generate endpoint."""
    model: str
    response: str
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None


@dataclass
class ModelInfo:
    """Information about an available Ollama model."""
    name: str
    size: int
    modified_at: str
    digest: str


class OllamaClient:
    """
    Async client for interacting with local Ollama server.
    
    Supports:
    - Text generation with streaming
    - Model listing and health checks
    - Proper error handling and timeouts
    - Connection pooling via aiohttp
    
    Example:
        async with OllamaClient() as client:
            response = await client.generate(
                model="llama3.2:3b",
                prompt="Explain AI orchestration",
                system="You are a helpful coding assistant."
            )
            print(response.response)
    """
    
    DEFAULT_BASE_URL = "http://localhost:11434"
    DEFAULT_TIMEOUT = 300  # 5 minutes for large model inference
    
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: URL of Ollama server (default: http://localhost:11434)
            timeout: Request timeout in seconds (default: 300)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def _ensure_session(self):
        """Create aiohttp session if not exists."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
            
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
            
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None,
    ) -> GenerateResponse:
        """
        Generate text completion from a model.
        
        Args:
            model: Name of the model (e.g., "llama3.2:3b")
            prompt: Input prompt text
            system: Optional system prompt for context
            temperature: Sampling temperature (0.0-1.0)
            stream: Whether to stream the response (not yet implemented)
            options: Additional model options
            
        Returns:
            GenerateResponse with model output and metadata
            
        Raises:
            ConnectionError: Cannot connect to Ollama server
            ModelNotFoundError: Model not available
            GenerationError: Generation failed
        """
        await self._ensure_session()
        
        # Build request payload
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,  # Non-streaming for now
            "options": {
                "temperature": temperature,
                **(options or {})
            }
        }
        
        if system:
            payload["system"] = system
            
        try:
            async with self._session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                
                # Handle HTTP errors
                if response.status == 404:
                    raise ModelNotFoundError(
                        f"Model '{model}' not found. "
                        f"Run 'ollama pull {model}' to download it."
                    )
                elif response.status >= 400:
                    error_text = await response.text()
                    raise GenerationError(
                        f"Generation failed (HTTP {response.status}): {error_text}"
                    )
                    
                # Parse response
                result = await response.json()
                
                return GenerateResponse(
                    model=result.get("model", model),
                    response=result.get("response", ""),
                    done=result.get("done", False),
                    total_duration=result.get("total_duration"),
                    load_duration=result.get("load_duration"),
                    prompt_eval_count=result.get("prompt_eval_count"),
                    eval_count=result.get("eval_count"),
                    eval_duration=result.get("eval_duration"),
                )
                
        except aiohttp.ClientConnectorError as e:
            raise ConnectionError(
                f"Cannot connect to Ollama server at {self.base_url}. "
                f"Is Ollama running? (ollama serve)"
            ) from e
        except aiohttp.ClientError as e:
            raise GenerationError(f"Request failed: {e}") from e
        except Exception as e:
            logger.exception("Unexpected error during generation")
            raise GenerationError(f"Unexpected error: {e}") from e
            
    async def generate_stream(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        options: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """
        Generate text with streaming (yields tokens as they arrive).
        
        Args:
            model: Name of the model
            prompt: Input prompt text
            system: Optional system prompt
            temperature: Sampling temperature
            options: Additional model options
            
        Yields:
            Text chunks as they are generated
            
        Raises:
            ConnectionError: Cannot connect to Ollama
            ModelNotFoundError: Model not available
            GenerationError: Generation failed
        """
        await self._ensure_session()
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                **(options or {})
            }
        }
        
        if system:
            payload["system"] = system
            
        try:
            async with self._session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                
                if response.status == 404:
                    raise ModelNotFoundError(f"Model '{model}' not found")
                elif response.status >= 400:
                    error_text = await response.text()
                    raise GenerationError(f"Generation failed: {error_text}")
                    
                # Stream the response
                async for line in response.content:
                    if line:
                        import json
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                yield chunk["response"]
                        except json.JSONDecodeError:
                            continue
                            
        except aiohttp.ClientConnectorError as e:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}"
            ) from e
        except aiohttp.ClientError as e:
            raise GenerationError(f"Stream failed: {e}") from e
            
    async def list_models(self) -> List[ModelInfo]:
        """
        List all available models on the Ollama server.
        
        Returns:
            List of ModelInfo objects
            
        Raises:
            ConnectionError: Cannot connect to Ollama
        """
        await self._ensure_session()
        
        try:
            async with self._session.get(
                f"{self.base_url}/api/tags"
            ) as response:
                
                if response.status >= 400:
                    error_text = await response.text()
                    raise GenerationError(
                        f"Failed to list models (HTTP {response.status}): {error_text}"
                    )
                    
                result = await response.json()
                models = result.get("models", [])
                
                return [
                    ModelInfo(
                        name=m["name"],
                        size=m["size"],
                        modified_at=m["modified_at"],
                        digest=m["digest"]
                    )
                    for m in models
                ]
                
        except aiohttp.ClientConnectorError as e:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}"
            ) from e
        except aiohttp.ClientError as e:
            raise GenerationError(f"Request failed: {e}") from e
            
    async def check_health(self) -> bool:
        """
        Check if Ollama server is running and accessible.
        
        Returns:
            True if server is healthy, False otherwise
        """
        await self._ensure_session()
        
        try:
            async with self._session.get(
                f"{self.base_url}/",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                # Ollama returns "Ollama is running" on root endpoint
                return response.status == 200
                
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False
            
    async def model_exists(self, model_name: str) -> bool:
        """
        Check if a specific model is available.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if model exists, False otherwise
        """
        try:
            models = await self.list_models()
            return any(m.name == model_name for m in models)
        except Exception:
            return False


# Convenience function for one-off requests
async def generate(
    model: str,
    prompt: str,
    system: Optional[str] = None,
    temperature: float = 0.7,
    base_url: str = OllamaClient.DEFAULT_BASE_URL,
) -> str:
    """
    Convenience function for one-off generation requests.
    
    Args:
        model: Model name
        prompt: Input prompt
        system: Optional system prompt
        temperature: Sampling temperature
        base_url: Ollama server URL
        
    Returns:
        Generated text as string
        
    Example:
        response = await generate(
            model="llama3.2:3b",
            prompt="What is AI orchestration?"
        )
    """
    async with OllamaClient(base_url=base_url) as client:
        result = await client.generate(
            model=model,
            prompt=prompt,
            system=system,
            temperature=temperature
        )
        return result.response


# Test function for manual testing
async def _test_connection():
    """Test Ollama connection and basic generation."""
    print("Testing Ollama connection...")
    
    async with OllamaClient() as client:
        # Check health
        healthy = await client.check_health()
        print(f"✅ Server health: {healthy}")
        
        if not healthy:
            print("❌ Ollama server not responding. Is it running?")
            return
            
        # List models
        models = await client.list_models()
        print(f"✅ Found {len(models)} models:")
        for model in models[:5]:  # Show first 5
            print(f"   - {model.name} ({model.size / 1e9:.1f} GB)")
            
        # Test generation with smallest model
        if models:
            test_model = models[0].name
            print(f"\n✅ Testing generation with {test_model}...")
            
            response = await client.generate(
                model=test_model,
                prompt="Say hello in one sentence.",
                temperature=0.7
            )
            
            print(f"✅ Response: {response.response}")
            print(f"✅ Tokens: {response.eval_count}")
            print(f"✅ Duration: {response.total_duration / 1e9:.2f}s")
        else:
            print("⚠️  No models found. Run 'ollama pull llama3.2:3b'")


if __name__ == "__main__":
    # Run test when executed directly
    asyncio.run(_test_connection())
