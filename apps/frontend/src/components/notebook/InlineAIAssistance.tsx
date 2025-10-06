'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Lightbulb, 
  Code, 
  Zap, 
  CheckCircle,
  X,
  ArrowRight,
  Wand2
} from 'lucide-react';

interface AISuggestion {
  id: string;
  type: 'completion' | 'optimization' | 'fix' | 'enhancement';
  title: string;
  description: string;
  code: string;
  confidence: number;
}

interface InlineAIAssistanceProps {
  cellContent: string;
  cellType: 'code' | 'markdown' | 'physics';
  cursorPosition: number;
  onAcceptSuggestion: (code: string) => void;
  onRejectSuggestion: () => void;
  isVisible: boolean;
}

export function InlineAIAssistance({
  cellContent,
  cellType,
  cursorPosition,
  onAcceptSuggestion,
  onRejectSuggestion,
  isVisible
}: InlineAIAssistanceProps) {
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);
  const [selectedSuggestion, setSelectedSuggestion] = useState<AISuggestion | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const generateSuggestions = (content: string, type: string): AISuggestion[] => {
    const suggestions: AISuggestion[] = [];

    // Code completion suggestions
    if (content.includes('import') && !content.includes('numpy')) {
      suggestions.push({
        id: '1',
        type: 'completion',
        title: 'Add NumPy import',
        description: 'NumPy is commonly used for numerical computations',
        code: 'import numpy as np',
        confidence: 0.9
      });
    }

    if (content.includes('plt') && !content.includes('import matplotlib')) {
      suggestions.push({
        id: '2',
        type: 'completion',
        title: 'Add Matplotlib import',
        description: 'Required for plotting functionality',
        code: 'import matplotlib.pyplot as plt',
        confidence: 0.95
      });
    }

    // Physics-specific suggestions
    if (type === 'physics' || content.includes('physics') || content.includes('simulation')) {
      if (content.includes('spring') && !content.includes('omega')) {
        suggestions.push({
          id: '3',
          type: 'enhancement',
          title: 'Add natural frequency calculation',
          description: 'Calculate the natural frequency of the spring-mass system',
          code: `# Natural frequency calculation
omega = np.sqrt(k/m)  # rad/s
frequency = omega / (2 * np.pi)  # Hz
period = 2 * np.pi / omega  # seconds`,
          confidence: 0.85
        });
      }

      if (content.includes('heat') && !content.includes('alpha')) {
        suggestions.push({
          id: '4',
          type: 'enhancement',
          title: 'Add thermal diffusivity',
          description: 'Essential parameter for heat transfer simulations',
          code: `# Thermal properties
alpha = k_thermal / (rho * c_p)  # thermal diffusivity (m²/s)
Pr = mu * c_p / k_thermal  # Prandtl number`,
          confidence: 0.8
        });
      }
    }

    // Code optimization suggestions
    if (content.includes('for') && content.includes('range') && content.includes('append')) {
      suggestions.push({
        id: '5',
        type: 'optimization',
        title: 'Vectorize loop operation',
        description: 'Replace loop with NumPy vectorized operation for better performance',
        code: `# Vectorized operation (faster than loops)
result = np.array([f(x) for x in input_array])
# or use numpy functions directly`,
        confidence: 0.75
      });
    }

    // Error fixes
    if (content.includes('math.') && !content.includes('import math')) {
      suggestions.push({
        id: '6',
        type: 'fix',
        title: 'Missing math import',
        description: 'Add missing import statement',
        code: 'import math',
        confidence: 0.98
      });
    }

    return suggestions;
  };

  useEffect(() => {
    if (isVisible && cellContent.length > 10) {
      setIsGenerating(true);
      
      // Simulate AI processing
      setTimeout(() => {
        const newSuggestions = generateSuggestions(cellContent, cellType);
        setSuggestions(newSuggestions);
        setSelectedSuggestion(newSuggestions[0] || null);
        setIsGenerating(false);
      }, 800);
    } else {
      setSuggestions([]);
      setSelectedSuggestion(null);
    }
  }, [cellContent, cellType, isVisible]);

  const getSuggestionIcon = (type: string) => {
    switch (type) {
      case 'completion': return <Code className="w-4 h-4" />;
      case 'optimization': return <Zap className="w-4 h-4" />;
      case 'fix': return <CheckCircle className="w-4 h-4" />;
      case 'enhancement': return <Sparkles className="w-4 h-4" />;
      default: return <Lightbulb className="w-4 h-4" />;
    }
  };

  const getSuggestionColor = (type: string) => {
    switch (type) {
      case 'completion': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'optimization': return 'text-green-600 bg-green-50 border-green-200';
      case 'fix': return 'text-red-600 bg-red-50 border-red-200';
      case 'enhancement': return 'text-purple-600 bg-purple-50 border-purple-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  if (!isVisible || (!isGenerating && suggestions.length === 0)) {
    return null;
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="absolute right-4 top-4 z-10 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <Wand2 className="w-4 h-4 text-purple-500" />
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              AI Suggestions
            </span>
          </div>
          <button
            onClick={onRejectSuggestion}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-3">
          {isGenerating ? (
            <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
              <Sparkles className="w-4 h-4 animate-pulse" />
              <span className="text-sm">Analyzing your code...</span>
            </div>
          ) : selectedSuggestion ? (
            <div className="space-y-3">
              {/* Selected suggestion */}
              <div className={`p-3 rounded-lg border ${getSuggestionColor(selectedSuggestion.type)}`}>
                <div className="flex items-start space-x-2">
                  {getSuggestionIcon(selectedSuggestion.type)}
                  <div className="flex-1">
                    <h4 className="text-sm font-medium">{selectedSuggestion.title}</h4>
                    <p className="text-xs mt-1 opacity-75">{selectedSuggestion.description}</p>
                    
                    {/* Code preview */}
                    <div className="mt-2 p-2 bg-gray-900 rounded text-xs text-white font-mono overflow-x-auto">
                      <pre>{selectedSuggestion.code}</pre>
                    </div>
                    
                    {/* Confidence */}
                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center space-x-1">
                        <span className="text-xs opacity-75">Confidence:</span>
                        <div className="w-16 h-1 bg-gray-200 rounded">
                          <div 
                            className="h-1 bg-current rounded" 
                            style={{ width: `${selectedSuggestion.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-xs opacity-75">
                          {Math.round(selectedSuggestion.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-2">
                <button
                  onClick={() => onAcceptSuggestion(selectedSuggestion.code)}
                  className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
                >
                  <CheckCircle className="w-3 h-3" />
                  <span>Accept</span>
                </button>
                <button
                  onClick={onRejectSuggestion}
                  className="px-3 py-2 text-gray-600 dark:text-gray-400 text-sm rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  Dismiss
                </button>
              </div>

              {/* Other suggestions */}
              {suggestions.length > 1 && (
                <div className="space-y-1">
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Other suggestions:
                  </div>
                  {suggestions.filter(s => s.id !== selectedSuggestion.id).map((suggestion) => (
                    <button
                      key={suggestion.id}
                      onClick={() => setSelectedSuggestion(suggestion)}
                      className="w-full flex items-center space-x-2 p-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded transition-colors"
                    >
                      {getSuggestionIcon(suggestion.type)}
                      <span className="text-sm text-gray-700 dark:text-gray-300">
                        {suggestion.title}
                      </span>
                      <ArrowRight className="w-3 h-3 text-gray-400 ml-auto" />
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : null}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}