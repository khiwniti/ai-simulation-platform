"""
Helper methods for the enhanced inline assistance service.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
import time

from .ai_providers.base_provider import CodeSuggestion, AIProviderResponse
from .ai_providers.provider_manager import ProviderStrategy
from .ai_providers.enhanced_context_analyzer import EnhancedCodeContext, CodeIntent
from .agents.base import AgentContext


class InlineAssistanceHelpers:
    """Helper methods for InlineAssistanceService."""
    
    @staticmethod
    def _map_trigger_to_suggestion_type(trigger_type: str) -> str:
        """Map frontend trigger type to AI provider suggestion type."""
        mapping = {
            'completion': 'completion',
            'hover': 'explanation',
            'manual': 'fix',
            'optimization': 'optimization'
        }
        return mapping.get(trigger_type, 'completion')
    
    @staticmethod
    def _select_provider_strategy(context: EnhancedCodeContext, trigger_type: str) -> ProviderStrategy:
        """Select the best AI provider strategy based on context."""
        # For syntax errors, prioritize accuracy
        if context.syntax_errors:
            return ProviderStrategy.MOST_ACCURATE
        
        # For completion, prioritize speed
        if trigger_type == 'completion':
            return ProviderStrategy.FASTEST_FIRST
        
        # For complex analysis, use redundant providers
        if (trigger_type == 'manual' and 
            context.complexity_score > 0.7 and 
            context.code_domain != 'general'):
            return ProviderStrategy.REDUNDANT
        
        # For explanations, prioritize accuracy
        if trigger_type == 'hover':
            return ProviderStrategy.MOST_ACCURATE
        
        # Default to cost-effective
        return ProviderStrategy.COST_EFFECTIVE
    
    @staticmethod
    def _convert_ai_response_to_suggestions(
        ai_response: AIProviderResponse,
        context: EnhancedCodeContext,
        trigger_type: str,
        session_id: UUID
    ) -> List[Dict[str, Any]]:
        """Convert AI provider response to frontend suggestion format."""
        suggestions = []
        
        if ai_response.error or not ai_response.suggestions:
            return suggestions
        
        for i, ai_suggestion in enumerate(ai_response.suggestions):
            suggestion_dict = {
                'id': str(uuid4()),
                'agent_id': ai_response.provider_name,
                'agent_type': 'ai_provider',
                'suggestion_type': InlineAssistanceHelpers._map_trigger_to_suggestion_type(trigger_type),
                'text': ai_suggestion.text,
                'insert_text': ai_suggestion.insert_text,
                'replace_range': ai_suggestion.replace_range,
                'confidence_score': ai_suggestion.confidence_score,
                'priority': InlineAssistanceHelpers._calculate_suggestion_priority(
                    ai_suggestion, context, trigger_type
                ),
                'explanation': ai_suggestion.explanation,
                'documentation': ai_suggestion.documentation,
                'metadata': {
                    'model_used': ai_response.model_used,
                    'processing_time': ai_response.processing_time,
                    'tokens_used': ai_response.tokens_used,
                    'provider': ai_response.provider_name,
                    'domain': context.code_domain,
                    'intent': context.detected_intent.value
                }
            }
            suggestions.append(suggestion_dict)
        
        return suggestions
    
    @staticmethod
    def _calculate_suggestion_priority(
        suggestion: CodeSuggestion,
        context: EnhancedCodeContext,
        trigger_type: str
    ) -> int:
        """Calculate priority for a suggestion based on context and type."""
        base_priority = 3
        
        # Higher priority for syntax error fixes
        if context.syntax_errors and 'error' in suggestion.text.lower():
            base_priority = 1
        
        # Higher priority for domain-specific suggestions
        if context.code_domain != 'general' and suggestion.confidence_score > 0.8:
            base_priority = min(base_priority, 2)
        
        # Completion suggestions get higher priority
        if trigger_type == 'completion':
            base_priority = min(base_priority, 2)
        
        # Adjust based on confidence
        if suggestion.confidence_score > 0.9:
            base_priority = max(1, base_priority - 1)
        elif suggestion.confidence_score < 0.5:
            base_priority = min(5, base_priority + 1)
        
        return base_priority
    
    @staticmethod
    def _sort_and_deduplicate_suggestions(suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort suggestions by priority and confidence, removing duplicates."""
        # Remove duplicates based on insert_text similarity
        unique_suggestions = []
        seen_texts = set()
        
        for suggestion in suggestions:
            text_key = suggestion.get('insert_text', suggestion.get('text', '')).strip().lower()
            if text_key and text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_suggestions.append(suggestion)
        
        # Sort by priority (lower is better) then by confidence (higher is better)
        unique_suggestions.sort(key=lambda s: (
            s.get('priority', 5),
            -s.get('confidence_score', 0.0)
        ))
        
        return unique_suggestions
    
    @staticmethod
    async def _get_legacy_agent_suggestions(
        context: EnhancedCodeContext,
        session_id: UUID,
        notebook_id: UUID,
        cell_id: UUID,
        code_content: str,
        trigger_type: str,
        orchestrator,
        agent_registry
    ) -> List[Dict[str, Any]]:
        """Get suggestions from legacy agent system for fallback/enhancement."""
        suggestions = []
        
        try:
            # Determine which agents to use
            agent_types = []
            if context.syntax_errors:
                agent_types.append('debug')
            if context.code_domain == 'physics':
                agent_types.append('physics')
            elif context.code_domain == 'visualization':
                agent_types.append('visualization')
            
            # Create agent context
            agent_context = AgentContext(
                session_id=session_id,
                notebook_id=notebook_id,
                cell_id=cell_id,
                current_code=code_content,
                cursor_position=0
            )
            
            # Get suggestions from each agent
            for agent_type in agent_types:
                try:
                    agent = agent_registry.create_agent(agent_type)
                    if not agent.is_active:
                        await agent.initialize(agent_context)
                    
                    query = InlineAssistanceHelpers._create_legacy_agent_query(context, trigger_type)
                    response = await agent.process_query(query, agent_context)
                    
                    agent_suggestions = InlineAssistanceHelpers._convert_legacy_response_to_suggestions(
                        response, agent_type, trigger_type, context
                    )
                    suggestions.extend(agent_suggestions)
                    
                except Exception as e:
                    print(f"Error getting legacy suggestions from {agent_type}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error in legacy agent suggestions: {e}")
        
        return suggestions
    
    @staticmethod
    def _create_legacy_agent_query(context: EnhancedCodeContext, trigger_type: str) -> str:
        """Create query for legacy agent system."""
        if context.syntax_errors:
            return f"Fix syntax errors: {'; '.join(context.syntax_errors)}"
        elif context.potential_bugs:
            return f"Fix potential bugs: {'; '.join(context.potential_bugs)}"
        elif context.performance_issues:
            return f"Optimize performance: {'; '.join(context.performance_issues)}"
        else:
            return f"Analyze and improve code: {context.current_line}"
    
    @staticmethod
    def _convert_legacy_response_to_suggestions(
        response,
        agent_type: str,
        trigger_type: str,
        context: EnhancedCodeContext
    ) -> List[Dict[str, Any]]:
        """Convert legacy agent response to suggestions."""
        suggestions = []
        
        try:
            base_id = f"legacy_{agent_type}_{trigger_type}_{int(time.time() * 1000)}"
            
            # Handle code snippets
            if hasattr(response, 'code_snippets') and response.code_snippets:
                for i, snippet in enumerate(response.code_snippets):
                    suggestions.append({
                        'id': f"{base_id}_code_{i}",
                        'agent_id': response.agent_id if hasattr(response, 'agent_id') else agent_type,
                        'agent_type': f'legacy_{agent_type}',
                        'suggestion_type': 'completion',
                        'text': snippet.get('description', 'Legacy suggestion'),
                        'insert_text': snippet.get('code', ''),
                        'confidence_score': getattr(response, 'confidence_score', 0.7),
                        'priority': 4,  # Lower priority for legacy suggestions
                        'explanation': snippet.get('explanation'),
                        'documentation': snippet.get('documentation')
                    })
            
            # Handle general suggestions
            if hasattr(response, 'suggestions') and response.suggestions:
                for i, suggestion in enumerate(response.suggestions):
                    suggestions.append({
                        'id': f"{base_id}_suggestion_{i}",
                        'agent_id': getattr(response, 'agent_id', agent_type),
                        'agent_type': f'legacy_{agent_type}',
                        'suggestion_type': 'fix' if context.syntax_errors else 'optimization',
                        'text': suggestion,
                        'confidence_score': getattr(response, 'confidence_score', 0.7),
                        'priority': 4,  # Lower priority for legacy suggestions
                        'explanation': getattr(response, 'response', None)
                    })
        
        except Exception as e:
            print(f"Error converting legacy response: {e}")
        
        return suggestions
    
    @staticmethod
    async def _provide_feedback_to_systems(
        suggestion,
        session_id: UUID,
        feedback_type: str,
        reason: Optional[str] = None
    ):
        """Provide feedback to AI providers and agents."""
        try:
            # For now, this is a placeholder for feedback mechanisms
            # In a full implementation, this would:
            # 1. Send feedback to AI providers for model fine-tuning
            # 2. Update agent performance metrics
            # 3. Log feedback for analytics
            
            feedback_data = {
                'suggestion_id': suggestion.get('id') if hasattr(suggestion, 'get') else getattr(suggestion, 'id', None),
                'session_id': session_id,
                'feedback_type': feedback_type,
                'reason': reason,
                'timestamp': time.time()
            }
            
            # Log feedback (placeholder)
            print(f"Feedback logged: {feedback_data}")
            
        except Exception as e:
            print(f"Error providing feedback: {e}")
