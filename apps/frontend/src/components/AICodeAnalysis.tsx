import React, { useState, useEffect } from 'react';
import { aiCodeAnalysisService, CodeAnalysis, CodeOptimization, CodeIssue } from '../services/aiCodeAnalysisService';

interface AICodeAnalysisProps {
  code: string;
  onInsertCode?: (code: string) => void;
  className?: string;
}

interface AnalysisResult {
  analysis?: CodeAnalysis;
  optimizations?: CodeOptimization[];
  issues?: CodeIssue[];
  loading: boolean;
  error?: string;
}

const AICodeAnalysis: React.FC<AICodeAnalysisProps> = ({
  code,
  onInsertCode,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState<'analysis' | 'optimizations' | 'issues' | 'explain'>('analysis');
  const [result, setResult] = useState<AnalysisResult>({ loading: false });
  const [explanation, setExplanation] = useState<string>('');

  const runAnalysis = async () => {
    if (!code.trim()) return;

    setResult({ loading: true });
    
    try {
      const [analysisRes, optimizationsRes, issuesRes] = await Promise.all([
        aiCodeAnalysisService.analyzeCode(code),
        aiCodeAnalysisService.optimizeCode(code),
        aiCodeAnalysisService.detectIssues(code)
      ]);

      setResult({
        loading: false,
        analysis: analysisRes.analysis || analysisRes.fallback,
        optimizations: optimizationsRes.optimizations || optimizationsRes.fallback,
        issues: issuesRes.issues || issuesRes.fallback
      });
    } catch (error: any) {
      setResult({
        loading: false,
        error: error.message
      });
    }
  };

  const explainCode = async () => {
    if (!code.trim()) return;

    try {
      const response = await aiCodeAnalysisService.explainCode(code);
      if (response.explanation) {
        setExplanation(aiCodeAnalysisService.formatAnalysisResults({
          ...response.explanation,
          timestamp: new Date().toISOString(),
          metrics: { totalLines: 0, codeLines: 0, commentLines: 0, blankLines: 0, functions: 0, classes: 0, imports: 0 },
          suggestions: [],
          complexity: { cyclomatic: 0, interpretation: 'Low' },
          readability: { score: 0, averageLineLength: 0, interpretation: 'Good' },
          maintainability: { score: 0, interpretation: 'High' },
          performance: { issues: [], score: 0, interpretation: 'Good' }
        } as CodeAnalysis));
      }
    } catch (error: any) {
      setExplanation(`Error explaining code: ${error.message}`);
    }
  };

  const generateTests = async () => {
    if (!code.trim()) return;

    try {
      const response = await aiCodeAnalysisService.generateTests(code);
      if (response.tests && onInsertCode) {
        onInsertCode(response.tests.testCode);
      }
    } catch (error: any) {
      console.error('Test generation error:', error);
    }
  };

  useEffect(() => {
    if (activeTab === 'explain' && !explanation) {
      explainCode();
    }
  }, [activeTab, code]);

  const renderAnalysis = () => {
    if (!result.analysis) return null;

    const { metrics, complexity, readability, maintainability, performance } = result.analysis;

    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-lg">
            <h4 className="font-medium text-purple-800 dark:text-purple-200 mb-2">📊 Metrics</h4>
            <div className="text-sm space-y-1">
              <div>Total Lines: <span className="font-mono">{metrics.totalLines}</span></div>
              <div>Code Lines: <span className="font-mono">{metrics.codeLines}</span></div>
              <div>Functions: <span className="font-mono">{metrics.functions}</span></div>
            </div>
          </div>

          <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
            <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">🎯 Quality</h4>
            <div className="text-sm space-y-1">
              <div>Complexity: <span className="font-mono">{complexity.interpretation}</span></div>
              <div>Readability: <span className="font-mono">{readability.score}/10</span></div>
              <div>Maintainability: <span className="font-mono">{maintainability.score}/10</span></div>
            </div>
          </div>
        </div>

        {result.analysis.suggestions.length > 0 && (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg">
            <h4 className="font-medium text-yellow-800 dark:text-yellow-200 mb-2">💡 Suggestions</h4>
            <ul className="text-sm space-y-1">
              {result.analysis.suggestions.map((suggestion, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-yellow-600 dark:text-yellow-400">•</span>
                  <span>{suggestion.message}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  const renderOptimizations = () => {
    if (!result.optimizations || result.optimizations.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          ✅ No optimizations needed! Your code looks great.
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {result.optimizations.map((optimization, index) => (
          <div
            key={index}
            className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="font-medium flex items-center gap-2">
                <span>{aiCodeAnalysisService.getTypeIcon(optimization.type)}</span>
                {optimization.title}
              </h4>
              <span
                className="px-2 py-1 rounded text-xs font-medium"
                style={{
                  backgroundColor: aiCodeAnalysisService.getSeverityColor(optimization.severity) + '20',
                  color: aiCodeAnalysisService.getSeverityColor(optimization.severity)
                }}
              >
                {optimization.severity}
              </span>
            </div>
            
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
              {optimization.description}
            </p>

            {optimization.example && (
              <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded border-l-4 border-purple-500 mb-3">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Example:</div>
                <code className="text-sm">{optimization.example}</code>
              </div>
            )}

            <div className="text-sm font-medium text-green-600 dark:text-green-400">
              💪 Impact: {optimization.impact}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderIssues = () => {
    if (!result.issues || result.issues.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          ✅ No issues detected! Your code is clean.
        </div>
      );
    }

    const groupedIssues = result.issues.reduce((acc, issue) => {
      if (!acc[issue.type]) acc[issue.type] = [];
      acc[issue.type].push(issue);
      return acc;
    }, {} as Record<string, CodeIssue[]>);

    return (
      <div className="space-y-4">
        {Object.entries(groupedIssues).map(([type, issues]) => (
          <div key={type}>
            <h4 className="font-medium mb-3 flex items-center gap-2">
              <span>{aiCodeAnalysisService.getTypeIcon(type)}</span>
              {type.charAt(0).toUpperCase() + type.slice(1)}s
            </h4>
            
            <div className="space-y-2">
              {issues.map((issue, index) => (
                <div
                  key={index}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-3"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-medium text-sm">Line {issue.line}</div>
                    <span
                      className="px-2 py-1 rounded text-xs font-medium"
                      style={{
                        backgroundColor: aiCodeAnalysisService.getSeverityColor(issue.severity) + '20',
                        color: aiCodeAnalysisService.getSeverityColor(issue.severity)
                      }}
                    >
                      {issue.severity}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                    {issue.message}
                  </p>
                  
                  <div className="text-xs text-blue-600 dark:text-blue-400">
                    💡 {issue.suggestion}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderExplanation = () => {
    if (!explanation) {
      return (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full"></div>
          <span className="ml-2 text-gray-500 dark:text-gray-400">Explaining code...</span>
        </div>
      );
    }

    return (
      <div className="prose prose-sm dark:prose-invert max-w-none">
        <pre className="whitespace-pre-wrap text-sm bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
          {explanation}
        </pre>
      </div>
    );
  };

  return (
    <div className={`bg-white dark:bg-gray-900 rounded-lg shadow-lg ${className}`}>
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            🧠 AI Code Analysis
          </h3>
          
          <div className="flex gap-2">
            <button
              onClick={runAnalysis}
              disabled={result.loading || !code.trim()}
              className="px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50 text-sm"
            >
              {result.loading ? '🔄' : '🔍'} Analyze
            </button>
            
            <button
              onClick={generateTests}
              disabled={!code.trim()}
              className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 text-sm"
            >
              🧪 Generate Tests
            </button>
          </div>
        </div>

        <div className="flex gap-1">
          {[
            { id: 'analysis', label: '📊 Analysis', count: result.analysis ? 1 : 0 },
            { id: 'optimizations', label: '⚡ Optimize', count: result.optimizations?.length || 0 },
            { id: 'issues', label: '🔍 Issues', count: result.issues?.length || 0 },
            { id: 'explain', label: '📚 Explain', count: explanation ? 1 : 0 }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                activeTab === tab.id
                  ? 'bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              {tab.label}
              {tab.count > 0 && (
                <span className="ml-1 bg-purple-500 text-white text-xs px-1 rounded-full">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="p-4 max-h-96 overflow-y-auto">
        {result.loading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full"></div>
            <span className="ml-2 text-gray-500 dark:text-gray-400">Analyzing code...</span>
          </div>
        )}

        {result.error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="text-red-800 dark:text-red-200 font-medium">Analysis Error</div>
            <div className="text-red-600 dark:text-red-300 text-sm mt-1">{result.error}</div>
          </div>
        )}

        {!result.loading && !result.error && (
          <>
            {activeTab === 'analysis' && renderAnalysis()}
            {activeTab === 'optimizations' && renderOptimizations()}
            {activeTab === 'issues' && renderIssues()}
            {activeTab === 'explain' && renderExplanation()}
          </>
        )}

        {!result.loading && !result.error && !code.trim() && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            Write some code to see AI analysis results
          </div>
        )}
      </div>
    </div>
  );
};

export default AICodeAnalysis;