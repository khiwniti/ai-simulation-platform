"""
AI Provider Manager for managing multiple AI providers and intelligent routing.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from .base_provider import (
    BaseAIProvider, 
    AIProviderConfig, 
    AIProviderType,
    CodeSuggestionRequest, 
    CodeSuggestion, 
    AIProviderResponse
)
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .local_provider import LocalAIProvider


class ProviderStrategy(Enum):
    """Strategies for selecting AI providers."""
    FASTEST_FIRST = "fastest_first"
    MOST_ACCURATE = "most_accurate"
    COST_EFFECTIVE = "cost_effective"
    REDUNDANT = "redundant"  # Try multiple providers
    FAILOVER = "failover"  # Fallback to next provider on failure


@dataclass
class ProviderPerformance:
    """Track provider performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    average_response_time: float = 0.0
    average_confidence: float = 0.0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    error_rate: float = 0.0
    last_used: float = 0.0
    availability_score: float = 1.0


class AIProviderManager:
    """
    Manages multiple AI providers with intelligent routing, load balancing,
    and failover capabilities.
    
    Features:
    - Multiple provider support (OpenAI, Anthropic, Local)
    - Intelligent provider selection based on context and performance
    - Load balancing and rate limit management
    - Automatic failover and fallback strategies
    - Cost optimization and performance tracking
    - Parallel processing for redundant strategies
    """
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.provider_configs: Dict[str, AIProviderConfig] = {}
        self.performance_metrics: Dict[str, ProviderPerformance] = {}
        self.default_strategy = ProviderStrategy.FAILOVER
        self.enabled_providers: List[str] = []
        
        # Provider preferences for different types of requests
        self.strategy_preferences = {
            ProviderStrategy.FASTEST_FIRST: ["local", "openai", "anthropic"],
            ProviderStrategy.MOST_ACCURATE: ["anthropic", "openai", "local"],
            ProviderStrategy.COST_EFFECTIVE: ["local", "openai", "anthropic"],
            ProviderStrategy.FAILOVER: ["openai", "anthropic", "local"],
            ProviderStrategy.REDUNDANT: ["openai", "anthropic"]
        }
        
        # Request type to strategy mapping
        self.request_strategy_map = {
            "completion": ProviderStrategy.FASTEST_FIRST,
            "explanation": ProviderStrategy.MOST_ACCURATE,
            "fix": ProviderStrategy.MOST_ACCURATE,
            "optimization": ProviderStrategy.REDUNDANT
        }
    
    async def initialize(self, provider_configs: Dict[str, AIProviderConfig]) -> None:
        """Initialize all configured providers."""
        self.provider_configs = provider_configs
        
        for provider_name, config in provider_configs.items():
            try:
                provider = self._create_provider(config)
                success = await provider.initialize()
                
                if success:
                    self.providers[provider_name] = provider
                    self.performance_metrics[provider_name] = ProviderPerformance()
                    self.enabled_providers.append(provider_name)
                    print(f"✓ Initialized {provider_name} provider")
                else:
                    print(f"✗ Failed to initialize {provider_name} provider")
                    
            except Exception as e:
                print(f"✗ Error initializing {provider_name} provider: {e}")
        
        if not self.enabled_providers:
            # Ensure we always have a fallback
            await self._initialize_fallback_provider()
    
    async def get_suggestions(
        self, 
        request: CodeSuggestionRequest,
        strategy: Optional[ProviderStrategy] = None,
        preferred_providers: Optional[List[str]] = None
    ) -> AIProviderResponse:
        """
        Get code suggestions using the specified strategy.
        
        Args:
            request: Code suggestion request
            strategy: Provider selection strategy
            preferred_providers: List of preferred provider names
            
        Returns:
            AIProviderResponse with suggestions from selected provider(s)
        """
        if not self.enabled_providers:
            return AIProviderResponse(
                suggestions=[],
                processing_time=0,
                tokens_used=0,
                model_used="none",
                provider_name="none",
                error="No providers available"
            )
        
        # Determine strategy
        if strategy is None:
            strategy = self.request_strategy_map.get(
                request.suggestion_type, 
                self.default_strategy
            )
        
        # Get provider ordering
        provider_order = self._get_provider_order(strategy, preferred_providers)
        
        if strategy == ProviderStrategy.REDUNDANT:
            return await self._get_redundant_suggestions(request, provider_order)
        else:
            return await self._get_sequential_suggestions(request, provider_order)
    
    async def get_streaming_suggestions(
        self, 
        request: CodeSuggestionRequest,
        provider_name: Optional[str] = None
    ):
        """Get streaming suggestions from a specific provider."""
        if provider_name and provider_name in self.providers:
            provider = self.providers[provider_name]
        else:
            # Use the fastest available provider for streaming
            provider_order = self._get_provider_order(ProviderStrategy.FASTEST_FIRST)
            if not provider_order:
                return
            provider = self.providers[provider_order[0]]
        
        try:
            async for suggestion in provider.get_streaming_suggestions(request):
                yield suggestion
        except Exception as e:
            print(f"Streaming error with {provider.provider_type}: {e}")
    
    def get_provider_statistics(self) -> Dict[str, Any]:
        """Get statistics for all providers."""
        stats = {
            "enabled_providers": self.enabled_providers,
            "total_providers": len(self.providers),
            "default_strategy": self.default_strategy.value,
            "providers": {}
        }
        
        for name, provider in self.providers.items():
            provider_stats = provider.get_statistics()
            performance = self.performance_metrics.get(name, ProviderPerformance())
            
            stats["providers"][name] = {
                **provider_stats,
                "performance": {
                    "total_requests": performance.total_requests,
                    "success_rate": (performance.successful_requests / max(performance.total_requests, 1)),
                    "average_response_time": performance.average_response_time,
                    "average_confidence": performance.average_confidence,
                    "total_tokens_used": performance.total_tokens_used,
                    "total_cost": performance.total_cost,
                    "error_rate": performance.error_rate,
                    "availability_score": performance.availability_score
                }
            }
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health checks on all providers."""
        health_results = {}
        
        tasks = []
        for name, provider in self.providers.items():
            tasks.append(self._provider_health_check(name, provider))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, (name, _) in enumerate(self.providers.items()):
                if isinstance(results[i], Exception):
                    health_results[name] = {
                        "status": "error",
                        "error": str(results[i])
                    }
                else:
                    health_results[name] = results[i]
        
        return health_results
    
    def set_default_strategy(self, strategy: ProviderStrategy) -> None:
        """Set the default provider selection strategy."""
        self.default_strategy = strategy
    
    def enable_provider(self, provider_name: str) -> bool:
        """Enable a specific provider."""
        if provider_name in self.providers and provider_name not in self.enabled_providers:
            self.enabled_providers.append(provider_name)
            return True
        return False
    
    def disable_provider(self, provider_name: str) -> bool:
        """Disable a specific provider."""
        if provider_name in self.enabled_providers:
            self.enabled_providers.remove(provider_name)
            return True
        return False
    
    def _create_provider(self, config: AIProviderConfig) -> BaseAIProvider:
        """Create a provider instance based on configuration."""
        if config.provider_type == AIProviderType.OPENAI:
            return OpenAIProvider(config)
        elif config.provider_type == AIProviderType.ANTHROPIC:
            return AnthropicProvider(config)
        elif config.provider_type == AIProviderType.LOCAL:
            return LocalAIProvider(config)
        else:
            raise ValueError(f"Unknown provider type: {config.provider_type}")
    
    async def _initialize_fallback_provider(self) -> None:
        """Initialize local fallback provider."""
        try:
            config = AIProviderConfig(
                provider_type=AIProviderType.LOCAL,
                model_name="local-fallback"
            )
            provider = LocalAIProvider(config)
            await provider.initialize()
            
            self.providers["local"] = provider
            self.performance_metrics["local"] = ProviderPerformance()
            self.enabled_providers.append("local")
            print("✓ Initialized fallback local provider")
            
        except Exception as e:
            print(f"✗ Failed to initialize fallback provider: {e}")
    
    def _get_provider_order(
        self, 
        strategy: ProviderStrategy,
        preferred_providers: Optional[List[str]] = None
    ) -> List[str]:
        """Get ordered list of providers based on strategy."""
        if preferred_providers:
            # Filter to only enabled providers
            return [p for p in preferred_providers if p in self.enabled_providers]
        
        # Get base order from strategy preferences
        base_order = self.strategy_preferences.get(strategy, self.enabled_providers)
        
        # Filter to enabled providers and add any missing ones
        ordered_providers = [p for p in base_order if p in self.enabled_providers]
        missing_providers = [p for p in self.enabled_providers if p not in ordered_providers]
        ordered_providers.extend(missing_providers)
        
        # Apply strategy-specific sorting
        if strategy == ProviderStrategy.FASTEST_FIRST:
            ordered_providers.sort(key=lambda p: self.performance_metrics[p].average_response_time)
        elif strategy == ProviderStrategy.MOST_ACCURATE:
            ordered_providers.sort(key=lambda p: -self.performance_metrics[p].average_confidence)
        elif strategy == ProviderStrategy.COST_EFFECTIVE:
            ordered_providers.sort(key=lambda p: self.performance_metrics[p].total_cost)
        
        return ordered_providers
    
    async def _get_sequential_suggestions(
        self, 
        request: CodeSuggestionRequest,
        provider_order: List[str]
    ) -> AIProviderResponse:
        """Get suggestions sequentially from providers until success."""
        last_error = None
        
        for provider_name in provider_order:
            if provider_name not in self.providers:
                continue
            
            provider = self.providers[provider_name]
            performance = self.performance_metrics[provider_name]
            
            try:
                start_time = time.time()
                response = await provider.get_code_suggestions(request)
                
                # Update performance metrics
                self._update_performance_metrics(
                    provider_name, response, start_time, success=not response.error
                )
                
                if not response.error and response.suggestions:
                    return response
                else:
                    last_error = response.error or "No suggestions returned"
                    
            except Exception as e:
                last_error = str(e)
                self._update_performance_metrics(
                    provider_name, None, start_time, success=False
                )
        
        # All providers failed
        return AIProviderResponse(
            suggestions=[],
            processing_time=0,
            tokens_used=0,
            model_used="none",
            provider_name="none",
            error=f"All providers failed. Last error: {last_error}"
        )
    
    async def _get_redundant_suggestions(
        self, 
        request: CodeSuggestionRequest,
        provider_order: List[str]
    ) -> AIProviderResponse:
        """Get suggestions from multiple providers and combine results."""
        tasks = []
        
        # Limit to first 2-3 providers for redundancy
        for provider_name in provider_order[:3]:
            if provider_name in self.providers:
                provider = self.providers[provider_name]
                tasks.append(self._get_provider_suggestions(provider_name, provider, request))
        
        if not tasks:
            return AIProviderResponse(
                suggestions=[],
                processing_time=0,
                tokens_used=0,
                model_used="none",
                provider_name="none",
                error="No providers available for redundant strategy"
            )
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine successful results
        all_suggestions = []
        total_tokens = 0
        total_time = 0
        providers_used = []
        
        for i, result in enumerate(results):
            if isinstance(result, AIProviderResponse) and not result.error:
                all_suggestions.extend(result.suggestions)
                total_tokens += result.tokens_used
                total_time = max(total_time, result.processing_time)
                providers_used.append(result.provider_name)
        
        # Sort by confidence and remove duplicates
        unique_suggestions = self._deduplicate_suggestions(all_suggestions)
        unique_suggestions.sort(key=lambda s: -s.confidence_score)
        
        return AIProviderResponse(
            suggestions=unique_suggestions[:request.max_suggestions],
            processing_time=total_time,
            tokens_used=total_tokens,
            model_used="multiple",
            provider_name="+".join(providers_used) if providers_used else "none"
        )
    
    async def _get_provider_suggestions(
        self, 
        provider_name: str, 
        provider: BaseAIProvider, 
        request: CodeSuggestionRequest
    ) -> AIProviderResponse:
        """Get suggestions from a single provider with error handling."""
        start_time = time.time()
        
        try:
            response = await provider.get_code_suggestions(request)
            self._update_performance_metrics(provider_name, response, start_time, True)
            return response
        except Exception as e:
            self._update_performance_metrics(provider_name, None, start_time, False)
            return AIProviderResponse(
                suggestions=[],
                processing_time=time.time() - start_time,
                tokens_used=0,
                model_used=provider.model_name,
                provider_name=provider_name,
                error=str(e)
            )
    
    def _deduplicate_suggestions(self, suggestions: List[CodeSuggestion]) -> List[CodeSuggestion]:
        """Remove duplicate suggestions based on text similarity."""
        unique_suggestions = []
        seen_texts = set()
        
        for suggestion in suggestions:
            # Simple deduplication based on text content
            text_key = suggestion.text.strip().lower()
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions
    
    def _update_performance_metrics(
        self, 
        provider_name: str, 
        response: Optional[AIProviderResponse], 
        start_time: float, 
        success: bool
    ) -> None:
        """Update performance metrics for a provider."""
        if provider_name not in self.performance_metrics:
            return
        
        performance = self.performance_metrics[provider_name]
        response_time = time.time() - start_time
        
        performance.total_requests += 1
        performance.last_used = time.time()
        
        if success and response:
            performance.successful_requests += 1
            performance.total_tokens_used += response.tokens_used
            
            # Update average response time
            performance.average_response_time = (
                (performance.average_response_time * (performance.total_requests - 1) + response_time) 
                / performance.total_requests
            )
            
            # Update average confidence
            if response.suggestions:
                avg_confidence = sum(s.confidence_score for s in response.suggestions) / len(response.suggestions)
                performance.average_confidence = (
                    (performance.average_confidence * (performance.successful_requests - 1) + avg_confidence)
                    / performance.successful_requests
                )
        
        # Update error rate
        performance.error_rate = 1.0 - (performance.successful_requests / performance.total_requests)
        
        # Update availability score (exponential moving average)
        alpha = 0.1
        if success:
            performance.availability_score = (1 - alpha) * performance.availability_score + alpha * 1.0
        else:
            performance.availability_score = (1 - alpha) * performance.availability_score + alpha * 0.0
    
    async def _provider_health_check(self, name: str, provider: BaseAIProvider) -> Dict[str, Any]:
        """Perform health check on a single provider."""
        try:
            health_result = await provider.health_check()
            health_result["provider_name"] = name
            return health_result
        except Exception as e:
            return {
                "provider_name": name,
                "status": "error",
                "error": str(e)
            }
