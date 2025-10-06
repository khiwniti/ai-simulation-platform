'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bot, 
  Send, 
  Sparkles, 
  Code, 
  Zap, 
  FileText,
  Lightbulb,
  ChevronRight,
  X,
  Minimize2,
  Maximize2,
  Settings,
  RefreshCw
} from 'lucide-react';
import AICodeAnalysis from '../AICodeAnalysis';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  suggestions?: string[];
}

interface AIAssistantSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentCellContent?: string;
  currentCellType?: 'code' | 'markdown' | 'physics';
  onInsertCode?: (code: string) => void;
}

export function AIAssistantSidebar({ 
  isOpen, 
  onClose, 
  currentCellContent = '', 
  currentCellType = 'code',
  onInsertCode 
}: AIAssistantSidebarProps) {
  const [activeTab, setActiveTab] = useState<'chat' | 'analysis'>('chat');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: `Welcome to EnsimuAI! 🤖 I'm your AI simulation assistant. I can help you with:

• Writing and optimizing simulation code
• Explaining physics concepts and equations
• Debugging and improving your models
• Suggesting best practices for engineering simulations

What would you like to work on today?`,
      timestamp: new Date(),
      suggestions: [
        'Help me create a fluid dynamics simulation',
        'Optimize my spring-mass system code',
        'Explain Navier-Stokes equations',
        'Generate heat transfer model'
      ]
    }
  ]);
  
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const simulateAIResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();
    
    // 3D Visualization and Geometry
    if (lowerMessage.includes('3d') || lowerMessage.includes('sphere') || lowerMessage.includes('cube') || 
        lowerMessage.includes('geometry') || lowerMessage.includes('visualization') || lowerMessage.includes('plot')) {
      return `Perfect! Here's a complete 3D visualization example with interactive sphere and cube geometry:

\`\`\`python
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Create figure and 3D axis
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Create a sphere
u = np.linspace(0, 2 * np.pi, 50)
v = np.linspace(0, np.pi, 50)
sphere_x = np.outer(np.cos(u), np.sin(v))
sphere_y = np.outer(np.sin(u), np.sin(v))
sphere_z = np.outer(np.ones(np.size(u)), np.cos(v))

# Create a cube
cube_size = 1.5
cube_coords = np.array([
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # bottom face
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # top face
]) * cube_size

# Plot sphere with colormap
ax.plot_surface(sphere_x, sphere_y, sphere_z, alpha=0.7, cmap='viridis')

# Plot cube edges
for i in range(4):
    # Bottom face edges
    ax.plot3D(*zip(cube_coords[i], cube_coords[(i+1)%4]), 'r-', linewidth=2)
    # Top face edges
    ax.plot3D(*zip(cube_coords[i+4], cube_coords[((i+1)%4)+4]), 'r-', linewidth=2)
    # Vertical edges
    ax.plot3D(*zip(cube_coords[i], cube_coords[i+4]), 'r-', linewidth=2)

# Styling and labels
ax.set_xlabel('X axis', fontsize=12)
ax.set_ylabel('Y axis', fontsize=12)
ax.set_zlabel('Z axis', fontsize=12)
ax.set_title('3D Geometric Visualization', fontsize=14, fontweight='bold')

# Set equal aspect ratio
ax.set_box_aspect([1,1,1])

plt.show()
\`\`\`

This creates an interactive 3D plot with both sphere and cube geometry. You can rotate and zoom the visualization!`;
    }
    
    if (lowerMessage.includes('fluid') || lowerMessage.includes('flow')) {
      return `Great! For fluid dynamics simulations, I recommend starting with the Navier-Stokes equations. Here's a basic setup:

\`\`\`python
import numpy as np
import matplotlib.pyplot as plt

# Fluid properties
rho = 1000  # density (kg/m³)
mu = 0.001  # dynamic viscosity (Pa·s)
Re = rho * U * L / mu  # Reynolds number

# Grid setup
nx, ny = 100, 100
dx, dy = 1.0/(nx-1), 1.0/(ny-1)
\`\`\`

Would you like me to help you implement the pressure-velocity coupling or boundary conditions?`;
    }
    
    if (lowerMessage.includes('spring') || lowerMessage.includes('mass')) {
      return `Perfect! Spring-mass systems are fundamental in mechanical simulations. Here's an enhanced version:

\`\`\`python
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

def spring_mass_system(y, t, m, k, c):
    x, v = y
    dxdt = v
    dvdt = -(k/m)*x - (c/m)*v  # includes damping
    return [dxdt, dvdt]

# System parameters
m = 1.0    # mass (kg)
k = 10.0   # spring constant (N/m)
c = 0.5    # damping coefficient
\`\`\`

This includes damping for more realistic behavior. Need help with the visualization?`;
    }
    
    if (lowerMessage.includes('heat') || lowerMessage.includes('thermal')) {
      return `Excellent choice! Heat transfer is crucial for many engineering applications. Here's a finite difference approach:

\`\`\`python
import numpy as np
import matplotlib.pyplot as plt

# Thermal properties
alpha = 1e-5  # thermal diffusivity (m²/s)
k_thermal = 400  # thermal conductivity (W/m·K)

# 2D heat equation solver
def heat_2d(T, alpha, dt, dx, dy):
    return T + alpha * dt * (
        (np.roll(T, 1, axis=0) - 2*T + np.roll(T, -1, axis=0))/dx**2 +
        (np.roll(T, 1, axis=1) - 2*T + np.roll(T, -1, axis=1))/dy**2
    )
\`\`\`

Would you like me to add boundary conditions or initial temperature distribution?`;
    }
    
    if (lowerMessage.includes('optimize') || lowerMessage.includes('improve')) {
      return `I can help optimize your simulation! Here are some key strategies:

**Performance Optimization:**
• Use vectorized operations with NumPy
• Implement adaptive time stepping
• Consider sparse matrices for large systems
• Use numba for JIT compilation

**Numerical Accuracy:**
• Check convergence criteria
• Validate against analytical solutions
• Use appropriate time step sizes
• Consider higher-order methods

**Code Quality:**
• Modularize your functions
• Add comprehensive documentation
• Implement error handling
• Create unit tests

What specific aspect would you like me to help optimize?`;
    }
    
    return `I understand you're working on "${userMessage}". Based on your current ${currentCellType} cell, I can help you with:

• Code implementation and optimization
• Physics equation derivation
• Parameter selection and tuning
• Visualization and plotting
• Error debugging and troubleshooting

Could you provide more specific details about what you'd like to accomplish?`;
  };

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    // Simulate AI processing delay
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: simulateAIResponse(inputText),
        timestamp: new Date(),
        suggestions: [
          'Generate complete code example',
          'Explain the physics behind this',
          'Optimize for better performance',
          'Add visualization code'
        ]
      };

      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1500);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputText(suggestion);
    inputRef.current?.focus();
  };

  const handleInsertCode = (code: string) => {
    const codeBlocks = code.match(/```[\s\S]*?```/g);
    if (codeBlocks && codeBlocks.length > 0) {
      const cleanCode = codeBlocks[0].replace(/```python\n?|```\n?/g, '');
      onInsertCode?.(cleanCode);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className={`fixed right-0 top-0 h-full bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700 shadow-2xl z-50 flex flex-col ${
        isMinimized ? 'w-16' : 'w-96'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
        {!isMinimized && (
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">EnsimuAI</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">Simulation Assistant</p>
            </div>
          </div>
        )}
        
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
          >
            {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
          </button>
          <button
            onClick={onClose}
            className="p-1 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      {!isMinimized && (
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'chat'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/10'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            💬 Chat
          </button>
          <button
            onClick={() => setActiveTab('analysis')}
            className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'analysis'
                ? 'text-purple-600 dark:text-purple-400 border-b-2 border-purple-600 dark:border-purple-400 bg-purple-50 dark:bg-purple-900/10'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            🧠 Analysis
          </button>
        </div>
      )}

      {!isMinimized && (
        <>
          {/* Content */}
          {activeTab === 'chat' && (
            <>
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                  <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] rounded-lg p-3 ${
                      message.type === 'user' 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white'
                    }`}>
                      <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                      
                      {/* Code block actions */}
                      {message.type === 'assistant' && message.content.includes('```') && (
                        <button
                          onClick={() => handleInsertCode(message.content)}
                          className="mt-2 text-xs bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600 transition-colors"
                        >
                          Insert Code
                        </button>
                      )}
                      
                      {/* Suggestions */}
                      {message.suggestions && message.suggestions.length > 0 && (
                        <div className="mt-3 space-y-1">
                          <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">Quick actions:</div>
                          {message.suggestions.map((suggestion, index) => (
                            <button
                              key={index}
                              onClick={() => handleSuggestionClick(suggestion)}
                              className="block w-full text-left text-xs bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 px-2 py-1 rounded hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-3">
                      <div className="flex items-center space-x-2">
                        <RefreshCw className="w-4 h-4 animate-spin text-blue-500" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">EnsimuAI is thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="border-t border-gray-200 dark:border-gray-700 p-4">
                <div className="flex space-x-2">
                  <textarea
                    ref={inputRef}
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask EnsimuAI about your simulation..."
                    className="flex-1 resize-none border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={2}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!inputText.trim() || isLoading}
                    className="px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </>
          )}

          {activeTab === 'analysis' && (
            <div className="flex-1 overflow-hidden">
              <AICodeAnalysis
                code={currentCellContent}
                onInsertCode={onInsertCode}
                className="h-full border-0 shadow-none"
              />
            </div>
          )}
        </>
      )}
    </motion.div>
  );
}