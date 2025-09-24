import { apiClient as api } from '../lib/api/client';

export interface CodeMetrics {
  totalLines: number;
  codeLines: number;
  commentLines: number;
  blankLines: number;
  functions: number;
  classes: number;
  imports: number;
}

export interface CodeSuggestion {
  type: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'info';
}

export interface ComplexityAnalysis {
  cyclomatic: number;
  interpretation: 'Low' | 'Medium' | 'High';
}

export interface ReadabilityAnalysis {
  score: number;
  averageLineLength: number;
  interpretation: 'Good' | 'Fair' | 'Needs Improvement';
}

export interface MaintainabilityAnalysis {
  score: number;
  interpretation: 'High' | 'Medium' | 'Low';
}

export interface PerformanceAnalysis {
  issues: string[];
  score: number;
  interpretation: 'Good' | 'Fair' | 'Needs Optimization';
}

export interface CodeAnalysis {
  timestamp: string;
  metrics: CodeMetrics;
  suggestions: CodeSuggestion[];
  complexity: ComplexityAnalysis;
  readability: ReadabilityAnalysis;
  maintainability: MaintainabilityAnalysis;
  performance: PerformanceAnalysis;
}

export interface CodeOptimization {
  type: 'performance' | 'memory' | 'quality' | 'general';
  severity: 'low' | 'medium' | 'high' | 'info';
  title: string;
  description: string;
  example?: string;
  impact: string;
}

export interface CodeExplanation {
  overview: string;
  lineByLine: Array<{
    lineNumber: number;
    code: string;
    explanation: string;
  }>;
  concepts: string[];
  algorithms: string[];
}

export interface CodeIssue {
  type: 'error' | 'warning' | 'info';
  severity: 'low' | 'medium' | 'high';
  line: number;
  message: string;
  suggestion: string;
}

export interface CodeTests {
  testCode: string;
  functions: Array<{
    name: string;
    signature: string;
  }>;
  coverage: string;
}

export interface AIAnalysisResponse {
  success: boolean;
  analysis?: CodeAnalysis;
  fallback?: any;
  error?: string;
}

export interface AIOptimizationResponse {
  success: boolean;
  optimizations?: CodeOptimization[];
  fallback?: CodeOptimization[];
  error?: string;
}

export interface AIExplanationResponse {
  success: boolean;
  explanation?: CodeExplanation;
  fallback?: any;
  error?: string;
}

export interface AIIssueResponse {
  success: boolean;
  issues?: CodeIssue[];
  fallback?: CodeIssue[];
  error?: string;
}

export interface AITestResponse {
  success: boolean;
  tests?: CodeTests;
  fallback?: any;
  error?: string;
}

export interface AIFeature {
  id: string;
  name: string;
  description: string;
  endpoint: string;
  methods: string[];
  parameters?: string[];
}

export interface AIFeaturesResponse {
  success: boolean;
  features: AIFeature[];
  version: string;
  status: string;
}

class AICodeAnalysisService {
  private baseURL = '/api/ai';

  /**
   * Analyze code for quality, performance, and best practices
   */
  async analyzeCode(code: string, context?: any): Promise<AIAnalysisResponse> {
    try {
      const response = await api.request('/ai/analyze-code', {
        method: 'POST',
        body: JSON.stringify({ code, context })
      });
      return response;
    } catch (error: any) {
      console.error('AI Code Analysis Error:', error);
      throw new Error(error.message || 'Failed to analyze code');
    }
  }

  /**
   * Get code optimization suggestions
   */
  async optimizeCode(
    code: string,
    optimizationType: 'performance' | 'memory' | 'quality' | 'all' = 'all'
  ): Promise<AIOptimizationResponse> {
    try {
      const response = await api.request('/ai/optimize-code', {
        method: 'POST',
        body: JSON.stringify({ code, optimizationType })
      });
      return response;
    } catch (error: any) {
      console.error('AI Code Optimization Error:', error);
      throw new Error(error.message || 'Failed to optimize code');
    }
  }

  /**
   * Get detailed code explanation
   */
  async explainCode(code: string): Promise<AIExplanationResponse> {
    try {
      const response = await api.request('/ai/explain-code', {
        method: 'POST',
        body: JSON.stringify({ code })
      });
      return response;
    } catch (error: any) {
      console.error('AI Code Explanation Error:', error);
      throw new Error(error.message || 'Failed to explain code');
    }
  }

  /**
   * Detect potential issues and bugs
   */
  async detectIssues(code: string): Promise<AIIssueResponse> {
    try {
      const response = await api.request('/ai/detect-issues', {
        method: 'POST',
        body: JSON.stringify({ code })
      });
      return response;
    } catch (error: any) {
      console.error('AI Issue Detection Error:', error);
      throw new Error(error.message || 'Failed to detect issues');
    }
  }

  /**
   * Generate unit tests for code
   */
  async generateTests(code: string): Promise<AITestResponse> {
    try {
      const response = await api.request('/ai/generate-tests', {
        method: 'POST',
        body: JSON.stringify({ code })
      });
      return response;
    } catch (error: any) {
      console.error('AI Test Generation Error:', error);
      throw new Error(error.message || 'Failed to generate tests');
    }
  }

  /**
   * Get available AI features
   */
  async getFeatures(): Promise<AIFeaturesResponse> {
    try {
      const response = await api.request('/ai/features', {
        method: 'GET'
      });
      return response;
    } catch (error: any) {
      console.error('AI Features Error:', error);
      throw new Error(error.message || 'Failed to get AI features');
    }
  }

  /**
   * Format analysis results for display
   */
  formatAnalysisResults(analysis: CodeAnalysis): string {
    const { metrics, complexity, readability, maintainability, performance } = analysis;
    
    return `
📊 **Code Metrics**
- Total Lines: ${metrics.totalLines}
- Code Lines: ${metrics.codeLines}
- Functions: ${metrics.functions}
- Classes: ${metrics.classes}

🔍 **Quality Analysis**
- Complexity: ${complexity.interpretation} (${complexity.cyclomatic})
- Readability: ${readability.interpretation} (${readability.score}/10)
- Maintainability: ${maintainability.interpretation} (${maintainability.score}/10)
- Performance: ${performance.interpretation} (${performance.score}/10)

💡 **Suggestions**
${analysis.suggestions.map(s => `- ${s.message}`).join('\n')}
    `.trim();
  }

  /**
   * Format optimization suggestions for display
   */
  formatOptimizations(optimizations: CodeOptimization[]): string {
    if (optimizations.length === 0) {
      return '✅ No major optimization opportunities found!';
    }

    return optimizations
      .map(opt => `
🔧 **${opt.title}** (${opt.severity} priority)
${opt.description}

${opt.example ? `\`\`\`python\n${opt.example}\n\`\`\`` : ''}

💪 **Impact**: ${opt.impact}
      `.trim())
      .join('\n\n');
  }

  /**
   * Format issues for display
   */
  formatIssues(issues: CodeIssue[]): string {
    if (issues.length === 0) {
      return '✅ No issues detected!';
    }

    const groupedIssues = issues.reduce((acc, issue) => {
      if (!acc[issue.type]) acc[issue.type] = [];
      acc[issue.type].push(issue);
      return acc;
    }, {} as Record<string, CodeIssue[]>);

    let result = '';
    
    if (groupedIssues.error) {
      result += '❌ **Errors**\n' + 
        groupedIssues.error.map(i => `Line ${i.line}: ${i.message}\n💡 ${i.suggestion}`).join('\n\n') + '\n\n';
    }
    
    if (groupedIssues.warning) {
      result += '⚠️ **Warnings**\n' + 
        groupedIssues.warning.map(i => `Line ${i.line}: ${i.message}\n💡 ${i.suggestion}`).join('\n\n') + '\n\n';
    }
    
    if (groupedIssues.info) {
      result += 'ℹ️ **Info**\n' + 
        groupedIssues.info.map(i => `Line ${i.line}: ${i.message}\n💡 ${i.suggestion}`).join('\n\n');
    }

    return result.trim();
  }

  /**
   * Get severity color for UI display
   */
  getSeverityColor(severity: 'low' | 'medium' | 'high' | 'info'): string {
    switch (severity) {
      case 'high': return '#ef4444'; // red
      case 'medium': return '#f59e0b'; // yellow
      case 'low': return '#10b981'; // green
      case 'info': return '#3b82f6'; // blue
      default: return '#6b7280'; // gray
    }
  }

  /**
   * Get type icon for UI display
   */
  getTypeIcon(type: string): string {
    switch (type) {
      case 'performance': return '⚡';
      case 'memory': return '💾';
      case 'quality': return '✨';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      case 'documentation': return '📚';
      case 'structure': return '🏗️';
      default: return '🔧';
    }
  }
}

export const aiCodeAnalysisService = new AICodeAnalysisService();