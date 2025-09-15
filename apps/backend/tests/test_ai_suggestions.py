"""
Comprehensive tests for the AI-powered suggestion system.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4, UUID
from datetime import datetime

from app.services.inline_assistance_service import InlineAssistanceService
from app.services.ai_providers.provider_manager import AIProviderManager, ProviderStrategy
from app.services.ai_providers.base_provider import (
    AIProviderConfig, 
    AIProviderType, 
    CodeSuggestionRequest, 
    CodeSuggestion, 
    AIProviderResponse
)
from app.services.ai_providers.enhanced_context_analyzer import (
    EnhancedContextAnalyzer, 
    EnhancedCodeContext,
    CodeIntent
)


class TestEnhancedContextAnalyzer:
    """Test the enhanced code context analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        return EnhancedContextAnalyzer()
    
    @pytest.mark.asyncio
    async def test_analyze_simple_code(self, analyzer):
        """Test analysis of simple Python code."""
        code = """
import numpy as np
import matplotlib.pyplot as plt

def calculate_physics():
    mass = 1.0
    force = 9.8
    acceleration = force / mass
    return acceleration

# Test function
result = calculate_physics()
print(f"Acceleration: {result}")
"""
        
        context = await analyzer.analyze_context(code, 150, 8, 10)
        
        assert context.code_domain == "physics"
        assert "numpy" in context.imported_modules
        assert "matplotlib.pyplot" in context.imported_modules
        assert context.current_function is not None
        assert context.current_function.name == "calculate_physics"
        assert len(context.local_variables) > 0
        assert context.detected_intent in [CodeIntent.VARIABLE_ASSIGNMENT, CodeIntent.COMPLETION]
        assert context.analysis_confidence > 0.7
    
    @pytest.mark.asyncio
    async def test_detect_syntax_errors(self, analyzer):
        """Test syntax error detection."""
        code = """
def broken_function(
    print("Missing closing parenthesis"
    return value
"""
        
        context = await analyzer.analyze_context(code, 50, 3, 5)
        
        assert len(context.syntax_errors) > 0
        assert context.analysis_confidence < 0.7
    
    @pytest.mark.asyncio
    async def test_visualization_code_detection(self, analyzer):
        """Test detection of visualization code."""
        code = """
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()
x = np.linspace(0, 10, 100)
y = np.sin(x)
ax.plot(x, y)
plt.show()
"""
        
        context = await analyzer.analyze_context(code, 80, 5, 0)
        
        assert context.code_domain == "visualization"
        assert "matplotlib" in context.frameworks_detected
        assert "numpy" in context.frameworks_detected
    
    @pytest.mark.asyncio
    async def test_complexity_calculation(self, analyzer):
        """Test complexity score calculation."""
        simple_code = "x = 1"
        complex_code = """
def complex_function(data):
    if len(data) > 0:
        for item in data:
            if item > 0:
                for i in range(item):
                    if i % 2 == 0:
                        yield i
                    else:
                        continue
            elif item < 0:
                raise ValueError("Negative values not allowed")
        return True
    else:
        return False
"""
        
        simple_context = await analyzer.analyze_context(simple_code, 5, 1, 5)
        complex_context = await analyzer.analyze_context(complex_code, 200, 8, 10)
        
        assert simple_context.complexity_score < complex_context.complexity_score
        assert complex_context.complexity_score > 0.5


class TestAIProviderManager:
    """Test the AI provider manager."""
    
    @pytest.fixture
    async def provider_manager(self):
        manager = AIProviderManager()
        
        # Mock provider configs
        configs = {
            'mock_openai': AIProviderConfig(
                provider_type=AIProviderType.OPENAI,
                model_name='gpt-3.5-turbo',
                api_key='mock-key'
            ),
            'mock_local': AIProviderConfig(
                provider_type=AIProviderType.LOCAL,
                model_name='local-model'
            )
        }
        
        with patch.object(manager, '_create_provider') as mock_create:
            # Mock provider instances
            mock_provider = Mock()
            mock_provider.initialize = AsyncMock(return_value=True)
            mock_provider.provider_type = AIProviderType.OPENAI
            mock_provider.model_name = 'gpt-3.5-turbo'
            mock_create.return_value = mock_provider
            
            await manager.initialize(configs)
        
        return manager
    
    @pytest.mark.asyncio
    async def test_provider_initialization(self, provider_manager):
        """Test provider initialization."""
        assert len(provider_manager.enabled_providers) == 2
        assert 'mock_openai' in provider_manager.enabled_providers
        assert 'mock_local' in provider_manager.enabled_providers
    
    @pytest.mark.asyncio
    async def test_suggestion_request(self, provider_manager):
        """Test getting suggestions from providers."""
        # Mock provider response
        mock_suggestions = [
            CodeSuggestion(
                text="Suggestion 1",
                insert_text="code1",
                confidence_score=0.9,
                suggestion_type="completion"
            ),
            CodeSuggestion(
                text="Suggestion 2", 
                insert_text="code2",
                confidence_score=0.8,
                suggestion_type="optimization"
            )
        ]
        
        mock_response = AIProviderResponse(
            suggestions=mock_suggestions,
            processing_time=100,
            tokens_used=50,
            model_used="gpt-3.5-turbo",
            provider_name="mock_openai"
        )
        
        # Mock provider method
        for provider in provider_manager.providers.values():
            provider.get_code_suggestions = AsyncMock(return_value=mock_response)
        
        request = CodeSuggestionRequest(
            code_content="def test():",
            cursor_position=10,
            line_number="def test():",
            suggestion_type="completion"
        )
        
        response = await provider_manager.get_suggestions(request)
        
        assert len(response.suggestions) == 2
        assert response.provider_name in provider_manager.enabled_providers
        assert response.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_redundant_strategy(self, provider_manager):
        """Test redundant provider strategy."""
        # Mock different responses from different providers
        responses = [
            AIProviderResponse(
                suggestions=[CodeSuggestion(
                    text="Provider 1 suggestion",
                    insert_text="code1",
                    confidence_score=0.9,
                    suggestion_type="completion"
                )],
                processing_time=100,
                tokens_used=30,
                model_used="gpt-3.5-turbo",
                provider_name="mock_openai"
            ),
            AIProviderResponse(
                suggestions=[CodeSuggestion(
                    text="Provider 2 suggestion",
                    insert_text="code2", 
                    confidence_score=0.8,
                    suggestion_type="completion"
                )],
                processing_time=150,
                tokens_used=40,
                model_used="local-model",
                provider_name="mock_local"
            )
        ]
        
        # Mock providers to return different responses
        provider_names = list(provider_manager.providers.keys())
        for i, provider in enumerate(provider_manager.providers.values()):
            provider.get_code_suggestions = AsyncMock(return_value=responses[i])
        
        request = CodeSuggestionRequest(
            code_content="def test():",
            cursor_position=10,
            line_number="def test():",
            suggestion_type="completion"
        )
        
        response = await provider_manager.get_suggestions(
            request, 
            strategy=ProviderStrategy.REDUNDANT
        )
        
        # Should combine suggestions from multiple providers
        assert len(response.suggestions) == 2
        assert "+" in response.provider_name  # Indicates multiple providers used
    
    @pytest.mark.asyncio
    async def test_health_check(self, provider_manager):
        """Test provider health check."""
        # Mock health check responses
        for provider in provider_manager.providers.values():
            provider.health_check = AsyncMock(return_value={
                "status": "healthy",
                "model": provider.model_name,
                "response_time": 50
            })
        
        health = await provider_manager.health_check()
        
        assert len(health) == len(provider_manager.enabled_providers)
        for provider_name in provider_manager.enabled_providers:
            assert health[provider_name]["status"] == "healthy"


class TestInlineAssistanceService:
    """Test the enhanced inline assistance service."""
    
    @pytest.fixture
    async def service(self):
        service = InlineAssistanceService()
        
        # Mock the provider manager
        service.provider_manager = Mock()
        service.provider_manager.get_suggestions = AsyncMock()
        service.provider_manager.get_provider_statistics = Mock(return_value={})
        service.provider_manager.health_check = AsyncMock(return_value={})
        
        # Mock the context analyzer
        service.context_analyzer = Mock()
        service.context_analyzer.analyze_context = AsyncMock()
        
        service._initialized = True
        return service
    
    @pytest.mark.asyncio
    async def test_analyze_code_context(self, service):
        """Test code context analysis."""
        # Mock enhanced context
        mock_context = EnhancedCodeContext(
            current_line="x = 1",
            current_word="x",
            cursor_column=1,
            preceding_code="",
            following_code="",
            ast_tree=None,
            syntax_errors=[],
            current_function=None,
            current_class=None,
            local_variables=[],
            global_variables=[],
            imported_modules=[],
            imported_functions=[],
            detected_intent=CodeIntent.VARIABLE_ASSIGNMENT,
            completion_context="variable assignment",
            code_domain="general",
            frameworks_detected=[],
            patterns_detected=[],
            complexity_score=0.1,
            style_issues=[],
            potential_bugs=[],
            performance_issues=[],
            function_calls=[],
            class_instantiations=[],
            data_flow={},
            analysis_confidence=0.9,
            processing_time=50
        )
        
        service.context_analyzer.analyze_context.return_value = mock_context
        
        result = await service.analyze_code_context("x = 1", 3, 1, 1)
        
        assert result['enhanced_context'] == mock_context
        assert result['confidence'] == 0.9
        assert 'processing_time' in result
    
    @pytest.mark.asyncio
    async def test_get_suggestions_completion(self, service):
        """Test getting completion suggestions."""
        # Mock context analysis
        mock_context = EnhancedCodeContext(
            current_line="np.",
            current_word="np",
            cursor_column=3,
            preceding_code="import numpy as np\n",
            following_code="",
            ast_tree=None,
            syntax_errors=[],
            current_function=None,
            current_class=None,
            local_variables=[],
            global_variables=[],
            imported_modules=["numpy"],
            imported_functions=[],
            detected_intent=CodeIntent.COMPLETION,
            completion_context="attributes/methods of np",
            code_domain="general",
            frameworks_detected=["numpy"],
            patterns_detected=[],
            complexity_score=0.1,
            style_issues=[],
            potential_bugs=[],
            performance_issues=[],
            function_calls=[],
            class_instantiations=[],
            data_flow={},
            analysis_confidence=0.9,
            processing_time=30
        )
        
        # Mock AI provider response
        mock_ai_response = AIProviderResponse(
            suggestions=[
                CodeSuggestion(
                    text="array() - Create a new array",
                    insert_text="array(",
                    confidence_score=0.95,
                    suggestion_type="completion"
                ),
                CodeSuggestion(
                    text="zeros() - Create array of zeros",
                    insert_text="zeros(",
                    confidence_score=0.90,
                    suggestion_type="completion"
                )
            ],
            processing_time=80,
            tokens_used=25,
            model_used="gpt-3.5-turbo",
            provider_name="openai"
        )
        
        service.provider_manager.get_suggestions.return_value = mock_ai_response
        
        context_analysis = {
            'enhanced_context': mock_context,
            'confidence': 0.9
        }
        
        suggestions = await service.get_suggestions(
            session_id=uuid4(),
            notebook_id=uuid4(), 
            cell_id=uuid4(),
            code_content="import numpy as np\nnp.",
            cursor_position=20,
            context_analysis=context_analysis,
            trigger_type='completion'
        )
        
        assert len(suggestions) == 2
        assert all(s['suggestion_type'] == 'completion' for s in suggestions)
        assert all(s['confidence_score'] > 0.8 for s in suggestions)
    
    @pytest.mark.asyncio
    async def test_apply_suggestion(self, service):
        """Test applying a suggestion."""
        suggestion_id = "test-suggestion-123"
        session_id = uuid4()
        
        # Add suggestion to cache
        mock_suggestion = {
            'id': suggestion_id,
            'text': 'Test suggestion',
            'insert_text': 'test_code()',
            'confidence_score': 0.9
        }
        service.suggestion_cache[suggestion_id] = mock_suggestion
        
        result = await service.apply_suggestion(suggestion_id, session_id)
        
        assert result['applied_text'] == 'test_code()'
        assert suggestion_id in service.applied_suggestions
        assert service.performance_stats['applied_suggestions'] == 1
    
    @pytest.mark.asyncio
    async def test_reject_suggestion(self, service):
        """Test rejecting a suggestion."""
        suggestion_id = "test-suggestion-456"
        session_id = uuid4()
        
        # Add suggestion to cache
        mock_suggestion = {
            'id': suggestion_id,
            'text': 'Test suggestion',
            'confidence_score': 0.5
        }
        service.suggestion_cache[suggestion_id] = mock_suggestion
        
        await service.reject_suggestion(suggestion_id, session_id, "Not relevant")
        
        assert suggestion_id in service.rejected_suggestions
        assert service.rejected_suggestions[suggestion_id]['reason'] == "Not relevant"
    
    def test_performance_stats(self, service):
        """Test performance statistics tracking."""
        initial_stats = service.get_performance_stats()
        
        assert 'total_requests' in initial_stats
        assert 'successful_suggestions' in initial_stats
        assert 'applied_suggestions' in initial_stats
        assert 'average_response_time' in initial_stats
    
    @pytest.mark.asyncio
    async def test_health_check(self, service):
        """Test service health check."""
        service.provider_manager.health_check.return_value = {
            'openai': {'status': 'healthy'},
            'local': {'status': 'healthy'}
        }
        
        health = await service.health_check()
        
        assert health['service_active'] == True
        assert health['service_initialized'] == True
        assert 'provider_health' in health


class TestIntegration:
    """Integration tests for the complete AI suggestion system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_physics_suggestion(self):
        """Test complete flow for physics code suggestions."""
        # This would be a more comprehensive test that:
        # 1. Initializes the full service with real (or mocked) AI providers
        # 2. Analyzes physics code context
        # 3. Gets domain-specific suggestions
        # 4. Applies feedback loop
        
        service = InlineAssistanceService()
        
        # Mock initialization to avoid real API calls in tests
        with patch.object(service, 'initialize') as mock_init:
            mock_init.return_value = True
            service._initialized = True
            
            # Mock the provider manager with physics-aware responses
            service.provider_manager = Mock()
            service.provider_manager.get_suggestions = AsyncMock(return_value=AIProviderResponse(
                suggestions=[
                    CodeSuggestion(
                        text="Create a physics world with gravity",
                        insert_text="world = physics.World(gravity=(0, -9.81, 0))",
                        confidence_score=0.95,
                        suggestion_type="completion"
                    )
                ],
                processing_time=120,
                tokens_used=40,
                model_used="gpt-4",
                provider_name="openai"
            ))
            
            # Mock context analyzer
            service.context_analyzer = Mock()
            service.context_analyzer.analyze_context = AsyncMock(return_value=EnhancedCodeContext(
                current_line="world = ",
                current_word="world",
                cursor_column=8,
                preceding_code="import physics\n",
                following_code="",
                ast_tree=None,
                syntax_errors=[],
                current_function=None,
                current_class=None,
                local_variables=[],
                global_variables=[],
                imported_modules=["physics"],
                imported_functions=[],
                detected_intent=CodeIntent.VARIABLE_ASSIGNMENT,
                completion_context="physics world creation",
                code_domain="physics",
                frameworks_detected=["physics"],
                patterns_detected=[],
                complexity_score=0.2,
                style_issues=[],
                potential_bugs=[],
                performance_issues=[],
                function_calls=[],
                class_instantiations=[],
                data_flow={},
                analysis_confidence=0.95,
                processing_time=45
            ))
            
            # Test the complete flow
            context_analysis = await service.analyze_code_context(
                "import physics\nworld = ", 25, 2, 8
            )
            
            suggestions = await service.get_suggestions(
                session_id=uuid4(),
                notebook_id=uuid4(),
                cell_id=uuid4(),
                code_content="import physics\nworld = ",
                cursor_position=25,
                context_analysis=context_analysis,
                trigger_type='completion'
            )
            
            assert len(suggestions) > 0
            assert suggestions[0]['suggestion_type'] == 'completion'
            assert 'physics' in suggestions[0]['insert_text'].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
