"""
Enhanced Inline AI Assistance Service for providing context-aware code suggestions.
"""

import asyncio
import re
import ast
import time
from typing import List, Dict, Any, Optional, Set, Tuple
from uuid import UUID, uuid4
from dataclasses import dataclass
from datetime import datetime

from .agents.orchestrator import AgentOrchestrator
from .agents.base import AgentContext, AgentCapability, agent_registry
from .ai_providers.provider_manager import AIProviderManager, ProviderStrategy
from .ai_providers.base_provider import (
    CodeSuggestionRequest, 
    CodeSuggestion, 
    AIProviderResponse,
    AIProviderConfig,
    AIProviderType
)
from .ai_providers.enhanced_context_analyzer import EnhancedContextAnalyzer, EnhancedCodeContext
from .inline_assistance_service_helpers import InlineAssistanceHelpers


@dataclass
class CodeContext:
    """Analyzed code context at cursor position."""
    current_line: str
    current_word: str
    preceding_code: str
    following_code: str
    function_context: Optional[str]
    class_context: Optional[str]
    import_statements: List[str]
    variables_in_scope: List[str]
    syntax_errors: List[str]
    code_type: str  # 'physics', 'visualization', 'general', 'math'
    indentation_level: int
    is_in_string: bool
    is_in_comment: bool


@dataclass
class SuggestionContext:
    """Context for generating suggestions."""
    trigger_type: str
    code_context: CodeContext
    cursor_position: int
    line_number: int
    column_number: int
    session_id: UUID
    notebook_id: UUID
    cell_id: UUID


class InlineAssistanceService:
    """
    Enhanced service for providing inline AI assistance with context-aware suggestions.
    
    Features:
    - Deep code context analysis using AST parsing
    - Multiple AI provider support (OpenAI, Anthropic, Local)
    - Intelligent provider selection based on context
    - Advanced suggestion types (completion, fix, optimization, explanation)
    - Real-time feedback and learning from user interactions
    """
    
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.provider_manager = AIProviderManager()
        self.context_analyzer = EnhancedContextAnalyzer()
        
        # Caching and feedback
        self.suggestion_cache: Dict[str, CodeSuggestion] = {}
        self.applied_suggestions: Dict[str, Dict[str, Any]] = {}
        self.rejected_suggestions: Dict[str, Dict[str, Any]] = {}
        self._active = True
        self._initialized = False
        
        # Performance tracking
        self.performance_stats = {
            'total_requests': 0,
            'successful_suggestions': 0,
            'applied_suggestions': 0,
            'average_response_time': 0.0
        }
    
    async def initialize(self, provider_configs: Optional[Dict[str, AIProviderConfig]] = None) -> bool:
        """Initialize the service with AI providers."""
        try:
            if not provider_configs:
                # Use default configurations
                provider_configs = {
                    'openai': AIProviderConfig(
                        provider_type=AIProviderType.OPENAI,
                        model_name='gpt-4',
                        api_key=None  # Will be loaded from environment
                    ),
                    'anthropic': AIProviderConfig(
                        provider_type=AIProviderType.ANTHROPIC,
                        model_name='claude-3-sonnet-20240229',
                        api_key=None  # Will be loaded from environment
                    ),
                    'local': AIProviderConfig(
                        provider_type=AIProviderType.LOCAL,
                        model_name='local-fallback'
                    )
                }
            
            await self.provider_manager.initialize(provider_configs)
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Failed to initialize InlineAssistanceService: {e}")
            return False

    async def analyze_code_context(
        self,
        code_content: str,
        cursor_position: int,
        line_number: int,
        column_number: int
    ) -> Dict[str, Any]:
        """
        Perform enhanced code context analysis using the advanced analyzer.
        
        Args:
            code_content: Full code content
            cursor_position: Absolute cursor position
            line_number: Current line number (1-based)
            column_number: Current column number (0-based)
            
        Returns:
            Dictionary containing enhanced context analysis
        """
        try:
            enhanced_context = await self.context_analyzer.analyze_context(
                code_content, cursor_position, line_number, column_number
            )
            
            return {
                'enhanced_context': enhanced_context,
                'processing_time': enhanced_context.processing_time,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'confidence': enhanced_context.analysis_confidence
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'processing_time': 0,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'confidence': 0.0
            }
    
    async def get_suggestions(
        self,
        session_id: UUID,
        notebook_id: UUID,
        cell_id: UUID,
        code_content: str,
        cursor_position: int,
        context_analysis: Dict[str, Any],
        trigger_type: str,
        additional_context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Get enhanced inline suggestions using AI providers and context analysis.
        
        Args:
            session_id: Session identifier
            notebook_id: Notebook identifier
            cell_id: Cell identifier
            code_content: Current code content
            cursor_position: Cursor position
            context_analysis: Pre-analyzed enhanced context
            trigger_type: Type of trigger ('completion', 'hover', 'manual')
            additional_context: Additional context information
            
        Returns:
            List of AI-powered suggestions
        """
        start_time = time.time()
        self.performance_stats['total_requests'] += 1
        
        try:
            if not self._initialized:
                await self.initialize()
            
            if 'enhanced_context' not in context_analysis:
                return []
                
            enhanced_context: EnhancedCodeContext = context_analysis['enhanced_context']
            
            # Skip suggestions in strings or comments for auto-completion
            if (trigger_type == 'completion' and 
                enhanced_context.current_line.strip().startswith(('#', '"""', "'''"))):
                return []
            
            # Create suggestion request
            suggestion_request = CodeSuggestionRequest(
                code_content=code_content,
                cursor_position=cursor_position,
                line_number=enhanced_context.current_line,
                suggestion_type=InlineAssistanceHelpers._map_trigger_to_suggestion_type(trigger_type),
                context=enhanced_context.completion_context,
                max_suggestions=5,
                include_explanations=(trigger_type in ['hover', 'manual']),
                domain_specific=enhanced_context.code_domain != 'general'
            )
            
            # Select AI provider strategy based on context
            strategy = InlineAssistanceHelpers._select_provider_strategy(enhanced_context, trigger_type)
            
            # Get suggestions from AI providers
            ai_response = await self.provider_manager.get_suggestions(
                suggestion_request, strategy
            )
            
            # Convert AI response to frontend format
            suggestions = InlineAssistanceHelpers._convert_ai_response_to_suggestions(
                ai_response, enhanced_context, trigger_type, session_id
            )
            
            # Cache AI suggestions
            for suggestion in suggestions:
                self.suggestion_cache[suggestion['id']] = suggestion
            
            # Enhance with agent-based suggestions if needed
            if trigger_type == 'manual' or enhanced_context.syntax_errors:
                agent_suggestions = await InlineAssistanceHelpers._get_legacy_agent_suggestions(
                    enhanced_context, session_id, notebook_id, cell_id, code_content, trigger_type,
                    self.orchestrator, agent_registry
                )
                suggestions.extend(agent_suggestions)
                
                # Cache agent suggestions
                for suggestion in agent_suggestions:
                    self.suggestion_cache[suggestion['id']] = suggestion
            
            # Sort and deduplicate
            suggestions = InlineAssistanceHelpers._sort_and_deduplicate_suggestions(suggestions)
            
            # Update performance stats
            self.performance_stats['successful_suggestions'] += len(suggestions)
            processing_time = time.time() - start_time
            self.performance_stats['average_response_time'] = (
                (self.performance_stats['average_response_time'] * 
                 (self.performance_stats['total_requests'] - 1) + processing_time) /
                self.performance_stats['total_requests']
            )
            
            return suggestions[:10]
            
        except Exception as e:
            print(f"Error getting suggestions: {e}")
            return []
    
    async def apply_suggestion(self, suggestion_id: str, session_id: UUID) -> Dict[str, Any]:
        """Apply an inline suggestion and record feedback for learning."""
        if suggestion_id not in self.suggestion_cache:
            raise ValueError(f"Suggestion {suggestion_id} not found")
        
        suggestion = self.suggestion_cache[suggestion_id]
        
        # Record application
        self.applied_suggestions[suggestion_id] = {
            'suggestion': suggestion.__dict__ if hasattr(suggestion, '__dict__') else suggestion,
            'session_id': session_id,
            'applied_at': datetime.utcnow()
        }
        
        # Update performance stats
        self.performance_stats['applied_suggestions'] += 1
        
        # Provide positive feedback to relevant systems
        await InlineAssistanceHelpers._provide_feedback_to_systems(suggestion, session_id, 'applied')
        
        return {
            'applied_text': suggestion.insert_text if hasattr(suggestion, 'insert_text') else suggestion.text,
            'suggestion': suggestion.__dict__ if hasattr(suggestion, '__dict__') else suggestion
        }
    
    async def reject_suggestion(
        self, 
        suggestion_id: str, 
        session_id: UUID, 
        reason: Optional[str] = None
    ) -> None:
        """Reject an inline suggestion and record feedback for learning."""
        if suggestion_id not in self.suggestion_cache:
            raise ValueError(f"Suggestion {suggestion_id} not found")
        
        suggestion = self.suggestion_cache[suggestion_id]
        
        # Record rejection
        self.rejected_suggestions[suggestion_id] = {
            'suggestion': suggestion.__dict__ if hasattr(suggestion, '__dict__') else suggestion,
            'session_id': session_id,
            'rejected_at': datetime.utcnow(),
            'reason': reason
        }
        
        # Provide negative feedback to relevant systems
        await InlineAssistanceHelpers._provide_feedback_to_systems(suggestion, session_id, 'rejected', reason)
    
    def is_active(self) -> bool:
        """Check if the service is active."""
        return self._active and self._initialized
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the service."""
        return {
            **self.performance_stats,
            'provider_stats': self.provider_manager.get_provider_statistics() if self._initialized else {},
            'cache_size': len(self.suggestion_cache),
            'applied_rate': (self.performance_stats['applied_suggestions'] / 
                           max(self.performance_stats['successful_suggestions'], 1))
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the service and its components."""
        health = {
            'service_active': self._active,
            'service_initialized': self._initialized,
            'cache_health': len(self.suggestion_cache) < 10000,  # Reasonable cache size
            'provider_health': {}
        }
        
        if self._initialized:
            health['provider_health'] = await self.provider_manager.health_check()
        
        return health
    
    def _get_word_at_position(self, line: str, column: int) -> str:
        """Get the word at the specified column position."""
        if column >= len(line):
            return ""
        
        # Find word boundaries
        start = column
        while start > 0 and (line[start-1].isalnum() or line[start-1] == '_'):
            start -= 1
        
        end = column
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        
        return line[start:end]
    
    def _get_function_context(self, code: str, line_number: int) -> Optional[str]:
        """Get the function context for the current line."""
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                        if node.lineno <= line_number <= (node.end_lineno or node.lineno):
                            return node.name
            
            return None
        except:
            return None
    
    def _get_class_context(self, code: str, line_number: int) -> Optional[str]:
        """Get the class context for the current line."""
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                        if node.lineno <= line_number <= (node.end_lineno or node.lineno):
                            return node.name
            
            return None
        except:
            return None
    
    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements from code."""
        imports = []
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}" if module else alias.name)
        except:
            pass
        
        return imports
    
    def _get_variables_in_scope(self, code: str, line_number: int) -> List[str]:
        """Get variables in scope at the specified line."""
        variables = []
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign) and hasattr(node, 'lineno'):
                    if node.lineno < line_number:
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                variables.append(target.id)
        except:
            pass
        
        return variables
    
    def _check_syntax_errors(self, code: str) -> List[str]:
        """Check for syntax errors in the code."""
        errors = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Line {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(str(e))
        
        return errors
    
    def _determine_code_type(self, code: str) -> str:
        """Determine the type of code based on content."""
        code_lower = code.lower()
        
        # Check for physics patterns
        physics_matches = sum(1 for pattern in self.physics_patterns 
                            if re.search(pattern, code_lower))
        
        # Check for visualization patterns
        viz_matches = sum(1 for pattern in self.viz_patterns 
                        if re.search(pattern, code_lower))
        
        # Check for math patterns
        math_matches = sum(1 for pattern in self.math_patterns 
                         if re.search(pattern, code_lower))
        
        # Determine primary type
        if physics_matches >= 2:
            return 'physics'
        elif viz_matches >= 2:
            return 'visualization'
        elif math_matches >= 2:
            return 'math'
        else:
            return 'general'
    
    def _is_in_string(self, code: str, position: int) -> bool:
        """Check if cursor position is inside a string literal."""
        if position >= len(code):
            return False
        
        # Simple check for string literals
        before_cursor = code[:position]
        single_quotes = before_cursor.count("'") - before_cursor.count("\\'")
        double_quotes = before_cursor.count('"') - before_cursor.count('\\"')
        
        return (single_quotes % 2 == 1) or (double_quotes % 2 == 1)
    
    def _is_in_comment(self, line: str, column: int) -> bool:
        """Check if cursor position is inside a comment."""
        comment_pos = line.find('#')
        return comment_pos != -1 and column >= comment_pos
    
    def _select_agents_for_context(self, code_context: Dict[str, Any], trigger_type: str) -> List[str]:
        """Select appropriate agents based on code context."""
        agents = []
        code_type = code_context.get('code_type', 'general')
        
        # Always include debug agent for syntax errors
        if code_context.get('syntax_errors'):
            agents.append('debug')
        
        # Select agents based on code type
        if code_type == 'physics':
            agents.extend(['physics', 'optimization'])
        elif code_type == 'visualization':
            agents.extend(['visualization', 'optimization'])
        elif code_type == 'math':
            agents.extend(['physics', 'optimization'])  # Physics agent handles math
        else:
            # For general code, use all agents but with lower priority
            if trigger_type == 'manual':
                agents.extend(['physics', 'visualization', 'optimization', 'debug'])
            else:
                agents.append('debug')  # Only debug for auto-completion
        
        return list(set(agents))  # Remove duplicates
    
    async def _get_agent_suggestions(
        self,
        agent_type: str,
        code_context: Dict[str, Any],
        agent_context: AgentContext,
        trigger_type: str
    ) -> List[Dict[str, Any]]:
        """Get suggestions from a specific agent type."""
        try:
            # Create or get agent
            agent = agent_registry.create_agent(agent_type)
            
            # Initialize if needed
            if not agent.is_active:
                await agent.initialize(agent_context)
            
            # Create query based on trigger type and context
            query = self._create_agent_query(code_context, trigger_type)
            
            # Get response from agent
            response = await agent.process_query(query, agent_context)
            
            # Convert response to suggestions
            suggestions = self._convert_response_to_suggestions(
                response, agent_type, trigger_type, code_context
            )
            
            # Cache suggestions
            for suggestion in suggestions:
                self.suggestion_cache[suggestion['id']] = suggestion
            
            return suggestions
            
        except Exception as e:
            print(f"Error getting suggestions from {agent_type}: {e}")
            return []
    
    def _create_agent_query(self, code_context: Dict[str, Any], trigger_type: str) -> str:
        """Create appropriate query for the agent based on context."""
        current_line = code_context.get('current_line', '')
        current_word = code_context.get('current_word', '')
        syntax_errors = code_context.get('syntax_errors', [])
        
        if trigger_type == 'completion':
            if current_word:
                return f"Provide code completion for '{current_word}' in context: {current_line}"
            else:
                return f"Provide code completion for line: {current_line}"
        elif trigger_type == 'hover':
            if current_word:
                return f"Explain '{current_word}' in context: {current_line}"
            else:
                return f"Explain code: {current_line}"
        elif trigger_type == 'manual':
            if syntax_errors:
                return f"Fix syntax errors: {'; '.join(syntax_errors)}"
            else:
                return f"Analyze and improve code: {current_line}"
        else:
            return f"Analyze code: {current_line}"
    
    def _convert_response_to_suggestions(
        self,
        response: Any,
        agent_type: str,
        trigger_type: str,
        code_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Convert agent response to inline suggestions."""
        suggestions = []
        
        try:
            # Generate unique ID for each suggestion
            base_id = f"{agent_type}_{trigger_type}_{int(time.time() * 1000)}"
            
            # Handle code snippets
            if hasattr(response, 'code_snippets') and response.code_snippets:
                for i, snippet in enumerate(response.code_snippets):
                    suggestions.append({
                        'id': f"{base_id}_code_{i}",
                        'agent_id': response.agent_id,
                        'agent_type': agent_type,
                        'suggestion_type': 'completion',
                        'text': snippet.get('description', 'Code suggestion'),
                        'insert_text': snippet.get('code', ''),
                        'confidence_score': response.confidence_score,
                        'priority': 1 if trigger_type == 'completion' else 2,
                        'explanation': snippet.get('explanation'),
                        'documentation': snippet.get('documentation')
                    })
            
            # Handle general suggestions
            if hasattr(response, 'suggestions') and response.suggestions:
                for i, suggestion in enumerate(response.suggestions):
                    suggestions.append({
                        'id': f"{base_id}_suggestion_{i}",
                        'agent_id': response.agent_id,
                        'agent_type': agent_type,
                        'suggestion_type': 'fix' if 'error' in suggestion.lower() else 'optimization',
                        'text': suggestion,
                        'confidence_score': response.confidence_score,
                        'priority': 2,
                        'explanation': response.response if hasattr(response, 'response') else None
                    })
            
            # Handle response text as explanation
            if hasattr(response, 'response') and response.response and trigger_type == 'hover':
                suggestions.append({
                    'id': f"{base_id}_explanation",
                    'agent_id': response.agent_id,
                    'agent_type': agent_type,
                    'suggestion_type': 'explanation',
                    'text': response.response,
                    'confidence_score': response.confidence_score,
                    'priority': 3,
                    'explanation': response.response
                })
            
        except Exception as e:
            print(f"Error converting response to suggestions: {e}")
        
        return suggestions
    
    async def _provide_agent_feedback(
        self,
        agent_id: str,
        session_id: UUID,
        feedback_type: str,
        suggestion_id: str,
        reason: Optional[str] = None
    ) -> None:
        """Provide feedback to an agent about suggestion usage."""
        try:
            agent = agent_registry.get_agent(agent_id)
            if agent and hasattr(agent, 'receive_feedback'):
                await agent.receive_feedback(
                    feedback_type=feedback_type,
                    suggestion_id=suggestion_id,
                    session_id=session_id,
                    reason=reason
                )
        except Exception as e:
            print(f"Error providing feedback to agent {agent_id}: {e}")