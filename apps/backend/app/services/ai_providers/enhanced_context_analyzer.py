"""
Enhanced Code Context Analyzer for AI-powered suggestions.
"""

import ast
import re
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class CodeIntent(Enum):
    """Types of coding intents detected from context."""
    COMPLETION = "completion"
    FUNCTION_DEF = "function_definition"
    CLASS_DEF = "class_definition"
    IMPORT_STATEMENT = "import_statement"
    VARIABLE_ASSIGNMENT = "variable_assignment"
    FUNCTION_CALL = "function_call"
    CONTROL_FLOW = "control_flow"
    ERROR_HANDLING = "error_handling"
    DOCUMENTATION = "documentation"
    ALGORITHM = "algorithm"
    DATA_STRUCTURE = "data_structure"


@dataclass
class CodeEntityInfo:
    """Information about a code entity (function, class, variable)."""
    name: str
    type: str  # 'function', 'class', 'variable', 'module'
    line_number: int
    scope: str  # 'global', 'class', 'function'
    signature: Optional[str] = None
    docstring: Optional[str] = None
    parameters: List[str] = None
    return_type: Optional[str] = None


@dataclass
class EnhancedCodeContext:
    """Enhanced code context with deep analysis."""
    # Basic context
    current_line: str
    current_word: str
    cursor_column: int
    preceding_code: str
    following_code: str
    
    # Structural analysis
    ast_tree: Optional[ast.AST]
    syntax_errors: List[str]
    
    # Scope analysis
    current_function: Optional[CodeEntityInfo]
    current_class: Optional[CodeEntityInfo]
    local_variables: List[CodeEntityInfo]
    global_variables: List[CodeEntityInfo]
    imported_modules: List[str]
    imported_functions: List[str]
    
    # Intent detection
    detected_intent: CodeIntent
    completion_context: str  # What the user is likely trying to complete
    
    # Domain-specific analysis
    code_domain: str  # 'physics', 'visualization', 'ml', 'web', 'general'
    frameworks_detected: List[str]
    patterns_detected: List[str]
    
    # Quality analysis
    complexity_score: float
    style_issues: List[str]
    potential_bugs: List[str]
    performance_issues: List[str]
    
    # Dependencies and relationships
    function_calls: List[str]
    class_instantiations: List[str]
    data_flow: Dict[str, List[str]]  # variable -> [dependencies]
    
    # Context metadata
    analysis_confidence: float
    processing_time: float


class EnhancedContextAnalyzer:
    """
    Advanced code context analyzer that provides deep understanding
    of code structure, intent, and domain for AI-powered suggestions.
    """
    
    def __init__(self):
        # Physics-related patterns
        self.physics_patterns = {
            'libraries': [r'physx_ai', r'pybullet', r'pymunk', r'numpy', r'scipy'],
            'concepts': [r'rigidbody', r'collision', r'force', r'velocity', r'acceleration', 
                        r'gravity', r'friction', r'mass', r'inertia', r'constraint'],
            'functions': [r'simulate', r'step', r'add_force', r'set_velocity', r'create_scene']
        }
        
        # Visualization patterns
        self.viz_patterns = {
            'libraries': [r'three\.js', r'matplotlib', r'plotly', r'seaborn', r'bokeh'],
            'concepts': [r'scene', r'camera', r'renderer', r'mesh', r'geometry', r'material',
                        r'plot', r'chart', r'graph', r'visualization', r'3d'],
            'functions': [r'render', r'plot', r'show', r'draw', r'animate', r'create_scene']
        }
        
        # Machine learning patterns
        self.ml_patterns = {
            'libraries': [r'tensorflow', r'pytorch', r'scikit-learn', r'keras', r'pandas'],
            'concepts': [r'model', r'training', r'dataset', r'neural', r'network', r'loss',
                        r'optimizer', r'accuracy', r'prediction', r'classification'],
            'functions': [r'fit', r'predict', r'train', r'evaluate', r'compile']
        }
        
        # Common code smells and issues
        self.code_smells = {
            'long_function': r'def\s+\w+\([^)]*\):[^}]*(?:\n[ \t]+[^\n]*){20,}',
            'magic_numbers': r'\b(?<![\.\w])\d{2,}\b(?![\.\w])',
            'nested_loops': r'for\s+.*?:\s*\n\s*for\s+.*?:',
            'deep_nesting': r'(\s{4}){4,}',
            'unused_import': r'import\s+(\w+)(?:.*\n(?!.*\1))*',
            'bare_except': r'except\s*:',
            'print_debugging': r'print\s*\(',
        }
    
    async def analyze_context(
        self,
        code_content: str,
        cursor_position: int,
        line_number: int,
        column_number: int
    ) -> EnhancedCodeContext:
        """Perform comprehensive code context analysis."""
        start_time = time.time()
        
        try:
            # Basic parsing
            lines = code_content.split('\n')
            current_line = lines[line_number - 1] if line_number <= len(lines) else ""
            current_word = self._get_word_at_position(current_line, column_number)
            
            # Get surrounding context
            preceding_code = '\n'.join(lines[:line_number-1]) if line_number > 1 else ""
            following_code = '\n'.join(lines[line_number:]) if line_number < len(lines) else ""
            
            # AST analysis
            ast_tree, syntax_errors = self._parse_ast(code_content)
            
            # Scope analysis
            current_function = self._get_current_function(ast_tree, line_number)
            current_class = self._get_current_class(ast_tree, line_number)
            local_variables = self._extract_local_variables(ast_tree, line_number)
            global_variables = self._extract_global_variables(ast_tree)
            imported_modules, imported_functions = self._extract_imports(ast_tree)
            
            # Intent detection
            detected_intent = self._detect_intent(current_line, preceding_code, cursor_position)
            completion_context = self._analyze_completion_context(
                current_line, current_word, column_number, detected_intent
            )
            
            # Domain analysis
            code_domain = self._detect_code_domain(code_content)
            frameworks_detected = self._detect_frameworks(code_content)
            patterns_detected = self._detect_patterns(code_content)
            
            # Quality analysis
            complexity_score = self._calculate_complexity(ast_tree)
            style_issues = self._detect_style_issues(code_content)
            potential_bugs = self._detect_potential_bugs(code_content, ast_tree)
            performance_issues = self._detect_performance_issues(code_content, ast_tree)
            
            # Dependency analysis
            function_calls = self._extract_function_calls(ast_tree)
            class_instantiations = self._extract_class_instantiations(ast_tree)
            data_flow = self._analyze_data_flow(ast_tree)
            
            # Calculate confidence
            analysis_confidence = self._calculate_analysis_confidence(
                ast_tree, syntax_errors, code_domain, detected_intent
            )
            
            processing_time = time.time() - start_time
            
            return EnhancedCodeContext(
                current_line=current_line,
                current_word=current_word,
                cursor_column=column_number,
                preceding_code=preceding_code,
                following_code=following_code,
                ast_tree=ast_tree,
                syntax_errors=syntax_errors,
                current_function=current_function,
                current_class=current_class,
                local_variables=local_variables,
                global_variables=global_variables,
                imported_modules=imported_modules,
                imported_functions=imported_functions,
                detected_intent=detected_intent,
                completion_context=completion_context,
                code_domain=code_domain,
                frameworks_detected=frameworks_detected,
                patterns_detected=patterns_detected,
                complexity_score=complexity_score,
                style_issues=style_issues,
                potential_bugs=potential_bugs,
                performance_issues=performance_issues,
                function_calls=function_calls,
                class_instantiations=class_instantiations,
                data_flow=data_flow,
                analysis_confidence=analysis_confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            # Return minimal context on error
            return EnhancedCodeContext(
                current_line=current_line if 'current_line' in locals() else "",
                current_word=current_word if 'current_word' in locals() else "",
                cursor_column=column_number,
                preceding_code="",
                following_code="",
                ast_tree=None,
                syntax_errors=[str(e)],
                current_function=None,
                current_class=None,
                local_variables=[],
                global_variables=[],
                imported_modules=[],
                imported_functions=[],
                detected_intent=CodeIntent.COMPLETION,
                completion_context="",
                code_domain="general",
                frameworks_detected=[],
                patterns_detected=[],
                complexity_score=0.0,
                style_issues=[],
                potential_bugs=[],
                performance_issues=[],
                function_calls=[],
                class_instantiations=[],
                data_flow={},
                analysis_confidence=0.1,
                processing_time=time.time() - start_time
            )
    
    def _get_word_at_position(self, line: str, column: int) -> str:
        """Extract word at cursor position."""
        if column >= len(line):
            return ""
        
        start = column
        while start > 0 and (line[start-1].isalnum() or line[start-1] in '_'):
            start -= 1
        
        end = column
        while end < len(line) and (line[end].isalnum() or line[end] in '_'):
            end += 1
        
        return line[start:end]
    
    def _parse_ast(self, code: str) -> Tuple[Optional[ast.AST], List[str]]:
        """Parse code into AST and collect syntax errors."""
        try:
            tree = ast.parse(code)
            return tree, []
        except SyntaxError as e:
            return None, [f"Line {e.lineno}: {e.msg}"]
        except Exception as e:
            return None, [str(e)]
    
    def _get_current_function(self, tree: Optional[ast.AST], line_number: int) -> Optional[CodeEntityInfo]:
        """Get the function containing the current line."""
        if not tree:
            return None
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    if node.lineno <= line_number <= (node.end_lineno or node.lineno):
                        # Extract function signature
                        args = [arg.arg for arg in node.args.args] if node.args else []
                        signature = f"{node.name}({', '.join(args)})"
                        
                        # Extract docstring
                        docstring = None
                        if (node.body and isinstance(node.body[0], ast.Expr) 
                            and isinstance(node.body[0].value, ast.Constant)
                            and isinstance(node.body[0].value.value, str)):
                            docstring = node.body[0].value.value
                        
                        return CodeEntityInfo(
                            name=node.name,
                            type="function",
                            line_number=node.lineno,
                            scope="global",
                            signature=signature,
                            docstring=docstring,
                            parameters=args
                        )
        
        return None
    
    def _get_current_class(self, tree: Optional[ast.AST], line_number: int) -> Optional[CodeEntityInfo]:
        """Get the class containing the current line."""
        if not tree:
            return None
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    if node.lineno <= line_number <= (node.end_lineno or node.lineno):
                        # Extract base classes
                        bases = []
                        for base in node.bases:
                            if isinstance(base, ast.Name):
                                bases.append(base.id)
                        
                        signature = f"{node.name}({', '.join(bases)})" if bases else node.name
                        
                        # Extract docstring
                        docstring = None
                        if (node.body and isinstance(node.body[0], ast.Expr) 
                            and isinstance(node.body[0].value, ast.Constant)
                            and isinstance(node.body[0].value.value, str)):
                            docstring = node.body[0].value.value
                        
                        return CodeEntityInfo(
                            name=node.name,
                            type="class",
                            line_number=node.lineno,
                            scope="global",
                            signature=signature,
                            docstring=docstring
                        )
        
        return None
    
    def _extract_local_variables(self, tree: Optional[ast.AST], line_number: int) -> List[CodeEntityInfo]:
        """Extract local variables in scope at the given line."""
        if not tree:
            return []
        
        variables = []
        
        # Find the containing function
        containing_function = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    if node.lineno <= line_number <= (node.end_lineno or node.lineno):
                        containing_function = node
                        break
        
        if not containing_function:
            return []
        
        # Extract assignments within the function
        for node in ast.walk(containing_function):
            if isinstance(node, ast.Assign) and hasattr(node, 'lineno'):
                if node.lineno < line_number:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            variables.append(CodeEntityInfo(
                                name=target.id,
                                type="variable",
                                line_number=node.lineno,
                                scope="local"
                            ))
        
        return variables
    
    def _extract_global_variables(self, tree: Optional[ast.AST]) -> List[CodeEntityInfo]:
        """Extract global variables."""
        if not tree:
            return []
        
        variables = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and hasattr(node, 'lineno'):
                # Check if this is a top-level assignment
                for parent in ast.walk(tree):
                    if isinstance(parent, (ast.FunctionDef, ast.ClassDef)):
                        if hasattr(parent, 'lineno') and hasattr(parent, 'end_lineno'):
                            if parent.lineno <= node.lineno <= (parent.end_lineno or parent.lineno):
                                break
                else:
                    # This is a global assignment
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            variables.append(CodeEntityInfo(
                                name=target.id,
                                type="variable",
                                line_number=node.lineno,
                                scope="global"
                            ))
        
        return variables
    
    def _extract_imports(self, tree: Optional[ast.AST]) -> Tuple[List[str], List[str]]:
        """Extract imported modules and functions."""
        if not tree:
            return [], []
        
        modules = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    modules.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    functions.append(f"{module}.{alias.name}" if module else alias.name)
        
        return modules, functions
    
    def _detect_intent(self, current_line: str, preceding_code: str, cursor_position: int) -> CodeIntent:
        """Detect the user's coding intent."""
        line_stripped = current_line.strip()
        
        # Check for specific patterns
        if line_stripped.startswith('def '):
            return CodeIntent.FUNCTION_DEF
        elif line_stripped.startswith('class '):
            return CodeIntent.CLASS_DEF
        elif line_stripped.startswith(('import ', 'from ')):
            return CodeIntent.IMPORT_STATEMENT
        elif '=' in current_line and not any(op in current_line for op in ['==', '!=', '<=', '>=']):
            return CodeIntent.VARIABLE_ASSIGNMENT
        elif any(keyword in line_stripped for keyword in ['if ', 'elif ', 'else:', 'for ', 'while ', 'with ']):
            return CodeIntent.CONTROL_FLOW
        elif any(keyword in line_stripped for keyword in ['try:', 'except ', 'finally:', 'raise ']):
            return CodeIntent.ERROR_HANDLING
        elif line_stripped.startswith(('"""', "'''", '#')):
            return CodeIntent.DOCUMENTATION
        elif '(' in current_line and ')' in current_line:
            return CodeIntent.FUNCTION_CALL
        else:
            return CodeIntent.COMPLETION
    
    def _analyze_completion_context(
        self, 
        current_line: str, 
        current_word: str, 
        column: int,
        intent: CodeIntent
    ) -> str:
        """Analyze what the user is trying to complete."""
        line_up_to_cursor = current_line[:column]
        
        if intent == CodeIntent.FUNCTION_CALL:
            # Look for function name before parentheses
            match = re.search(r'(\w+)\s*\(\s*$', line_up_to_cursor)
            if match:
                return f"arguments for {match.group(1)}()"
        
        if '.' in line_up_to_cursor:
            # Attribute access
            parts = line_up_to_cursor.split('.')
            if len(parts) >= 2:
                return f"attributes/methods of {parts[-2]}"
        
        if current_word:
            return f"completion for '{current_word}'"
        
        return "general completion"
    
    def _detect_code_domain(self, code: str) -> str:
        """Detect the primary domain of the code."""
        code_lower = code.lower()
        
        # Count domain-specific patterns
        physics_score = self._count_domain_patterns(code_lower, self.physics_patterns)
        viz_score = self._count_domain_patterns(code_lower, self.viz_patterns)
        ml_score = self._count_domain_patterns(code_lower, self.ml_patterns)
        
        # Determine primary domain
        max_score = max(physics_score, viz_score, ml_score)
        if max_score >= 2:
            if physics_score == max_score:
                return "physics"
            elif viz_score == max_score:
                return "visualization"
            elif ml_score == max_score:
                return "machine_learning"
        
        # Check for web development
        if any(term in code_lower for term in ['flask', 'django', 'fastapi', 'request', 'response']):
            return "web"
        
        return "general"
    
    def _count_domain_patterns(self, code: str, patterns: Dict[str, List[str]]) -> int:
        """Count patterns matching a specific domain."""
        score = 0
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, code):
                    score += 1
        return score
    
    def _detect_frameworks(self, code: str) -> List[str]:
        """Detect frameworks and libraries used in the code."""
        frameworks = []
        code_lower = code.lower()
        
        framework_patterns = {
            'numpy': r'import numpy|from numpy|np\.',
            'pandas': r'import pandas|from pandas|pd\.',
            'matplotlib': r'import matplotlib|from matplotlib|plt\.',
            'tensorflow': r'import tensorflow|from tensorflow|tf\.',
            'pytorch': r'import torch|from torch',
            'scikit-learn': r'from sklearn|import sklearn',
            'flask': r'from flask|import flask',
            'django': r'from django|import django',
            'fastapi': r'from fastapi|import fastapi',
            'three.js': r'three\.js|THREE\.',
            'physx': r'physx|physx_ai'
        }
        
        for framework, pattern in framework_patterns.items():
            if re.search(pattern, code_lower):
                frameworks.append(framework)
        
        return frameworks
    
    def _detect_patterns(self, code: str) -> List[str]:
        """Detect coding patterns and design patterns."""
        patterns = []
        
        # Design patterns
        if re.search(r'class\s+\w+Singleton', code):
            patterns.append("singleton_pattern")
        if re.search(r'class\s+\w+Factory', code):
            patterns.append("factory_pattern")
        if re.search(r'def\s+__enter__|def\s+__exit__', code):
            patterns.append("context_manager")
        
        # Coding patterns
        if re.search(r'\[.*for.*in.*\]', code):
            patterns.append("list_comprehension")
        if re.search(r'with\s+open\(', code):
            patterns.append("file_handling")
        if re.search(r'yield\s+', code):
            patterns.append("generator")
        if re.search(r'async\s+def|await\s+', code):
            patterns.append("async_programming")
        
        return patterns
    
    def _calculate_complexity(self, tree: Optional[ast.AST]) -> float:
        """Calculate cyclomatic complexity of the code."""
        if not tree:
            return 0.0
        
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity / 10.0  # Normalize to 0-1 range
    
    def _detect_style_issues(self, code: str) -> List[str]:
        """Detect PEP 8 and style issues."""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Line too long
            if len(line) > 88:
                issues.append(f"Line {i}: Line too long ({len(line)} characters)")
            
            # Trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(f"Line {i}: Trailing whitespace")
            
            # Missing space after comma
            if re.search(r',[^\s\]\})]', line):
                issues.append(f"Line {i}: Missing space after comma")
        
        return issues
    
    def _detect_potential_bugs(self, code: str, tree: Optional[ast.AST]) -> List[str]:
        """Detect potential bugs and issues."""
        bugs = []
        
        # Check for common code smells
        for smell, pattern in self.code_smells.items():
            if re.search(pattern, code, re.MULTILINE):
                bugs.append(f"Potential issue: {smell.replace('_', ' ')}")
        
        # AST-based checks
        if tree:
            for node in ast.walk(tree):
                # Unused variables (simple check)
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.startswith('_'):
                            bugs.append(f"Possibly unused variable: {target.id}")
        
        return bugs
    
    def _detect_performance_issues(self, code: str, tree: Optional[ast.AST]) -> List[str]:
        """Detect potential performance issues."""
        issues = []
        
        # String concatenation in loops
        if re.search(r'for\s+.*:\s*\n\s*.*\+=.*["\']', code, re.MULTILINE):
            issues.append("String concatenation in loop - consider using join()")
        
        # Inefficient list operations
        if '+=.*\\[' in code:
            issues.append("Consider using extend() instead of += for lists")
        
        # Global variable access in loops
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    # Check for global variable access in loop body
                    for child in ast.walk(node):
                        if isinstance(child, ast.Name) and child.id.isupper():
                            issues.append("Global variable access in loop may impact performance")
                            break
        
        return issues
    
    def _extract_function_calls(self, tree: Optional[ast.AST]) -> List[str]:
        """Extract function calls from the AST."""
        if not tree:
            return []
        
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(f"*.{node.func.attr}")
        
        return list(set(calls))
    
    def _extract_class_instantiations(self, tree: Optional[ast.AST]) -> List[str]:
        """Extract class instantiations from the AST."""
        if not tree:
            return []
        
        instantiations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id[0].isupper():
                    instantiations.append(node.func.id)
        
        return list(set(instantiations))
    
    def _analyze_data_flow(self, tree: Optional[ast.AST]) -> Dict[str, List[str]]:
        """Analyze data flow dependencies."""
        if not tree:
            return {}
        
        data_flow = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Get assignment targets
                targets = []
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        targets.append(target.id)
                
                # Get dependencies from the value
                dependencies = []
                for child in ast.walk(node.value):
                    if isinstance(child, ast.Name):
                        dependencies.append(child.id)
                
                # Record dependencies
                for target in targets:
                    data_flow[target] = dependencies
        
        return data_flow
    
    def _calculate_analysis_confidence(
        self, 
        tree: Optional[ast.AST], 
        syntax_errors: List[str],
        code_domain: str,
        detected_intent: CodeIntent
    ) -> float:
        """Calculate confidence in the analysis results."""
        confidence = 1.0
        
        # Reduce confidence for syntax errors
        if syntax_errors:
            confidence -= 0.3
        
        # Reduce confidence if AST parsing failed
        if not tree:
            confidence -= 0.4
        
        # Reduce confidence for unknown domain
        if code_domain == "general":
            confidence -= 0.1
        
        # Reduce confidence for completion intent (less specific)
        if detected_intent == CodeIntent.COMPLETION:
            confidence -= 0.1
        
        return max(0.1, confidence)
