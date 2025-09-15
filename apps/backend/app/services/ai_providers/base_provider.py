"""
Base AI Provider interface for code suggestions.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import time
import asyncio


class AIProviderType(Enum):
    """Types of AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    CUSTOM = "custom"


@dataclass
class AIProviderConfig:
    """Configuration for AI providers."""
    provider_type: AIProviderType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: str = "gpt-4"
    max_tokens: int = 2048
    temperature: float = 0.1
    timeout: float = 30.0
    max_retries: int = 3
    rate_limit_rpm: int = 60  # requests per minute
    rate_limit_tpm: int = 40000  # tokens per minute
    enable_streaming: bool = True
    enable_caching: bool = True
    cache_ttl: int = 300  # 5 minutes


@dataclass
class CodeSuggestionRequest:
    """Request for code suggestions."""
    code_context: str
    cursor_position: int
    suggestion_type: str  # 'completion', 'explanation', 'fix', 'optimization'
    language: str = "python"
    max_suggestions: int = 5
    include_documentation: bool = True
    additional_context: Dict[str, Any] = None


@dataclass
class CodeSuggestion:
    """A code suggestion from an AI provider."""
    id: str
    text: str
    insert_text: Optional[str] = None
    replace_range: Optional[Dict[str, int]] = None
    confidence_score: float = 0.8
    explanation: Optional[str] = None
    documentation: Optional[str] = None
    suggestion_type: str = "completion"
    provider_name: str = ""
    model_used: str = ""
    processing_time: float = 0.0
    tokens_used: int = 0


@dataclass
class AIProviderResponse:
    """Response from AI provider."""
    suggestions: List[CodeSuggestion]
    processing_time: float
    tokens_used: int
    model_used: str
    provider_name: str
    cached: bool = False
    rate_limited: bool = False
    error: Optional[str] = None


class BaseAIProvider(ABC):
    """
    Base class for AI providers that generate code suggestions.
    
    Implements common functionality like rate limiting, caching, retries,
    and token management while allowing providers to implement their
    specific AI model interactions.
    """
    
    def __init__(self, config: AIProviderConfig):
        self.config = config
        self.provider_type = config.provider_type
        self.model_name = config.model_name
        self.is_initialized = False
        
        # Rate limiting
        self._request_times: List[float] = []
        self._token_usage: List[tuple[float, int]] = []
        
        # Caching
        self._suggestion_cache: Dict[str, AIProviderResponse] = {}
        
        # Statistics
        self.total_requests = 0
        self.total_tokens_used = 0
        self.average_response_time = 0.0
        self.success_rate = 0.0
        self.error_count = 0
    
    async def initialize(self) -> bool:
        """Initialize the AI provider."""
        try:
            await self._initialize_provider()
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize {self.provider_type.value} provider: {e}")
            return False
    
    @abstractmethod
    async def _initialize_provider(self) -> None:
        """Provider-specific initialization."""
        pass
    
    async def get_code_suggestions(
        self, 
        request: CodeSuggestionRequest
    ) -> AIProviderResponse:
        """
        Get code suggestions with rate limiting, caching, and retries.
        """
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Check cache first
            if self.config.enable_caching:
                cache_key = self._create_cache_key(request)
                if cache_key in self._suggestion_cache:
                    cached_response = self._suggestion_cache[cache_key]
                    if time.time() - cached_response.processing_time < self.config.cache_ttl:
                        cached_response.cached = True
                        return cached_response
            
            # Check rate limits
            if await self._is_rate_limited():
                return AIProviderResponse(
                    suggestions=[],
                    processing_time=time.time() - start_time,
                    tokens_used=0,
                    model_used=self.model_name,
                    provider_name=self.provider_type.value,
                    rate_limited=True,
                    error="Rate limited"
                )
            
            # Get suggestions with retries
            response = await self._get_suggestions_with_retries(request)
            
            # Update statistics
            self._update_statistics(response, start_time)
            
            # Cache response
            if self.config.enable_caching and not response.error:
                cache_key = self._create_cache_key(request)
                self._suggestion_cache[cache_key] = response
            
            return response
            
        except Exception as e:
            self.error_count += 1
            return AIProviderResponse(
                suggestions=[],
                processing_time=time.time() - start_time,
                tokens_used=0,
                model_used=self.model_name,
                provider_name=self.provider_type.value,
                error=str(e)
            )
    
    async def get_streaming_suggestions(
        self, 
        request: CodeSuggestionRequest
    ) -> AsyncGenerator[CodeSuggestion, None]:
        """Get streaming code suggestions (if supported by provider)."""
        if not self.config.enable_streaming:
            # Fallback to regular suggestions
            response = await self.get_code_suggestions(request)
            for suggestion in response.suggestions:
                yield suggestion
            return
        
        try:
            async for suggestion in self._get_streaming_suggestions_impl(request):
                yield suggestion
        except Exception as e:
            print(f"Streaming suggestions failed: {e}")
            # Fallback to regular suggestions
            response = await self.get_code_suggestions(request)
            for suggestion in response.suggestions:
                yield suggestion
    
    @abstractmethod
    async def _get_suggestions_impl(
        self, 
        request: CodeSuggestionRequest
    ) -> AIProviderResponse:
        """Provider-specific implementation for getting suggestions."""
        pass
    
    async def _get_streaming_suggestions_impl(
        self, 
        request: CodeSuggestionRequest
    ) -> AsyncGenerator[CodeSuggestion, None]:
        """Provider-specific implementation for streaming suggestions."""
        # Default implementation - override in providers that support streaming
        response = await self._get_suggestions_impl(request)
        for suggestion in response.suggestions:
            yield suggestion
    
    async def _get_suggestions_with_retries(
        self, 
        request: CodeSuggestionRequest
    ) -> AIProviderResponse:
        """Get suggestions with retry logic."""
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                response = await asyncio.wait_for(
                    self._get_suggestions_impl(request),
                    timeout=self.config.timeout
                )
                return response
            except asyncio.TimeoutError:
                last_error = "Request timeout"
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                last_error = str(e)
                if "rate" in str(e).lower():
                    # Rate limit error - wait longer
                    await asyncio.sleep(60)
                else:
                    await asyncio.sleep(2 ** attempt)
        
        return AIProviderResponse(
            suggestions=[],
            processing_time=0,
            tokens_used=0,
            model_used=self.model_name,
            provider_name=self.provider_type.value,
            error=f"Max retries exceeded. Last error: {last_error}"
        )
    
    async def _is_rate_limited(self) -> bool:
        """Check if we're hitting rate limits."""
        current_time = time.time()
        
        # Clean old entries (older than 1 minute)
        self._request_times = [t for t in self._request_times if current_time - t < 60]
        self._token_usage = [(t, tokens) for t, tokens in self._token_usage if current_time - t < 60]
        
        # Check request rate limit
        if len(self._request_times) >= self.config.rate_limit_rpm:
            return True
        
        # Check token rate limit
        total_tokens_last_minute = sum(tokens for _, tokens in self._token_usage)
        if total_tokens_last_minute >= self.config.rate_limit_tpm:
            return True
        
        return False
    
    def _create_cache_key(self, request: CodeSuggestionRequest) -> str:
        """Create a cache key for the request."""
        import hashlib
        
        key_data = f"{request.code_context}_{request.cursor_position}_{request.suggestion_type}_{request.language}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _update_statistics(self, response: AIProviderResponse, start_time: float) -> None:
        """Update provider statistics."""
        self.total_requests += 1
        self.total_tokens_used += response.tokens_used
        
        processing_time = time.time() - start_time
        self.average_response_time = (
            (self.average_response_time * (self.total_requests - 1) + processing_time) 
            / self.total_requests
        )
        
        if not response.error:
            success_count = self.total_requests - self.error_count
            self.success_rate = success_count / self.total_requests
        
        # Update rate limiting tracking
        current_time = time.time()
        self._request_times.append(current_time)
        self._token_usage.append((current_time, response.tokens_used))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get provider statistics."""
        return {
            "provider_type": self.provider_type.value,
            "model_name": self.model_name,
            "is_initialized": self.is_initialized,
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
            "average_response_time": self.average_response_time,
            "success_rate": self.success_rate,
            "error_count": self.error_count,
            "cache_size": len(self._suggestion_cache),
            "rate_limit_status": {
                "requests_last_minute": len([t for t in self._request_times if time.time() - t < 60]),
                "tokens_last_minute": sum(tokens for t, tokens in self._token_usage if time.time() - t < 60),
                "requests_limit": self.config.rate_limit_rpm,
                "tokens_limit": self.config.rate_limit_tpm
            }
        }
    
    def clear_cache(self) -> None:
        """Clear the suggestion cache."""
        self._suggestion_cache.clear()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the provider."""
        try:
            # Simple test request
            test_request = CodeSuggestionRequest(
                code_context="print('hello')",
                cursor_position=5,
                suggestion_type="completion",
                max_suggestions=1
            )
            
            start_time = time.time()
            response = await self._get_suggestions_impl(test_request)
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if not response.error else "unhealthy",
                "response_time": response_time,
                "error": response.error,
                "suggestions_count": len(response.suggestions),
                "tokens_used": response.tokens_used
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": -1
            }
