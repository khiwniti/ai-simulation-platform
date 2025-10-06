'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Play, 
  Square, 
  Plus, 
  Save, 
  Download, 
  Share2, 
  Settings,
  Zap,
  Code,
  FileText,
  MoreVertical,
  ChevronDown,
  Bot,
  Sparkles
} from 'lucide-react';
import Link from 'next/link';
import { Button } from '../../../components/ui/button';
import { AIAssistantSidebar } from '../../../components/notebook/AIAssistantSidebar';
import { UserMenu } from '../../../components/ui/user-menu';
import { CellComponent } from '../../../components/notebook/SimpleCellComponent';
import { notebookService, NotebookData } from '../../../services/notebookService';

interface NotebookPageProps {
  params: {
    id: string;
  };
}

interface Cell {
  id: string;
  type: 'code' | 'markdown' | 'physics';
  content: string;
  output?: {
    text?: string;
    figures?: string[];
    error?: {
      type: string;
      message: string;
      traceback: string;
    };
  };
  isRunning?: boolean;
  executionId?: string;
}

export default function NotebookPage({ params }: NotebookPageProps) {
  const [notebook, setNotebook] = useState<NotebookData | null>(null);
  const [cells, setCells] = useState<Cell[]>([
    {
      id: '1',
      type: 'markdown',
      content: '# Engineering Simulation Notebook\n\nWelcome to **EnsimuNotebook** - AI-enhanced engineering simulation environment.\n\n## Quick Start:\n- **Code cells**: Write Python for data analysis and calculations\n- **Physics cells**: Build real-time 3D simulations with physics engines\n- **AI assistance**: Get intelligent code suggestions and optimizations\n- **Visualization**: Create interactive plots and 3D models\n\n💡 **Tip**: Click the AI assistant button (✨) for intelligent help at any time!'
    },
    {
      id: '2',
      type: 'code',
      content: '# Engineering Analysis Setup\nimport numpy as np\nimport matplotlib.pyplot as plt\nfrom scipy import optimize, integrate\n\n# Example: Structural beam analysis\nL = 10.0  # Length (m)\nE = 200e9  # Young\'s modulus (Pa) - steel\nI = 8.3e-6  # Second moment of area (m^4)\nw = 5000  # Distributed load (N/m)\n\n# Maximum deflection at center\nmax_deflection = (5 * w * L**4) / (384 * E * I)\nprint(f"Maximum beam deflection: {max_deflection*1000:.2f} mm")\n\n# Stress analysis\nmax_moment = w * L**2 / 8  # Maximum bending moment\nmax_stress = max_moment * (0.05) / I  # Assuming beam height = 0.1m\nprint(f"Maximum bending stress: {max_stress/1e6:.1f} MPa")'
    },
    {
      id: '3',
      type: 'physics',
      content: '// 3D Physics Simulation - Pendulum System\n// This cell creates an interactive 3D physics simulation\n\n// Define pendulum parameters\nconst pendulumLength = 5.0;\nconst mass = 1.0;\nconst gravity = 9.81;\nconst initialAngle = Math.PI / 4; // 45 degrees\n\n// Create 3D scene\nscene = new THREE.Scene();\ncamera = new THREE.PerspectiveCamera(75, 800/600, 0.1, 1000);\nrenderer = new THREE.WebGLRenderer();\n\n// Add pendulum visualization\nconst sphereGeometry = new THREE.SphereGeometry(0.2, 32, 32);\nconst sphereMaterial = new THREE.MeshPhongMaterial({ color: 0xff4444 });\nconst pendulumBob = new THREE.Mesh(sphereGeometry, sphereMaterial);\n\n// Physics simulation loop\nfunction simulate() {\n  // Pendulum physics equations\n  const angularAcceleration = -(gravity / pendulumLength) * Math.sin(currentAngle);\n  angularVelocity += angularAcceleration * deltaTime;\n  currentAngle += angularVelocity * deltaTime;\n  \n  // Update 3D position\n  pendulumBob.position.x = pendulumLength * Math.sin(currentAngle);\n  pendulumBob.position.y = -pendulumLength * Math.cos(currentAngle);\n}\n\nconsole.log("Interactive pendulum simulation ready!");'
    }
  ]);
  const [isRunning, setIsRunning] = useState(false);
  const [aiSidebarOpen, setAiSidebarOpen] = useState(false);
  const [currentCell, setCurrentCell] = useState<Cell | null>(null);
  const [loadingNotebook, setLoadingNotebook] = useState(true);

  useEffect(() => {
    async function loadNotebook() {
      try {
        setLoadingNotebook(true);
        // Try to load notebook from backend
        try {
          const notebookData = await notebookService.getNotebook(params.id);
          setNotebook(notebookData);
          if (notebookData.cells && notebookData.cells.length > 0) {
            setCells(notebookData.cells);
          }
        } catch (error) {
          console.log('Notebook not found in backend, using default cells');
          // Use default notebook if not found
          setNotebook({
            id: params.id,
            name: 'Engineering Simulation Workspace',
            description: 'AI-enhanced physics simulations and engineering analysis',
            template: 'engineering-simulation',
            type: 'physics',
            cells: [],
            createdAt: new Date().toISOString(),
            lastModified: new Date().toISOString(),
            metadata: {
              kernel: 'python3',
              language: 'python'
            }
          });
        }
      } catch (error) {
        console.error('Error loading notebook:', error);
      } finally {
        setLoadingNotebook(false);
      }
    }
    
    loadNotebook();
  }, [params.id]);

  const addCell = (type: 'code' | 'markdown' | 'physics', index?: number) => {
    const newCell: Cell = {
      id: Date.now().toString(),
      type,
      content: '',
    };

    if (index !== undefined) {
      const newCells = [...cells];
      newCells.splice(index + 1, 0, newCell);
      setCells(newCells);
    } else {
      setCells([...cells, newCell]);
    }
  };

  const updateCell = (cellId: string, content: string) => {
    setCells(cells.map(cell => 
      cell.id === cellId ? { ...cell, content } : cell
    ));
  };

  const deleteCell = (cellId: string) => {
    setCells(cells.filter(cell => cell.id !== cellId));
  };

  const runCell = async (cellId: string) => {
    const cell = cells.find(c => c.id === cellId);
    if (!cell) return;

    // Mark cell as running
    setCells(cells.map(c => 
      c.id === cellId ? { ...c, isRunning: true, output: undefined } : c
    ));

    try {
      let result;
      
      // For demo mode, use simple execution without notebook ID
      if (params.id === 'demo') {
        result = await notebookService.executeCodeSimple(cell.content);
        
        // Update cell with results (simple execution format)
        setCells(prevCells => prevCells.map(c => {
          if (c.id === cellId) {
            return {
              ...c,
              isRunning: false,
              output: {
                text: result.output,
                figures: result.figures || [],
                error: result.error
              }
            };
          }
          return c;
        }));
      } else {
        // For real notebooks, use normal execution with notebook ID
        if (!notebook) return;
        
        const execResult = await notebookService.executeCode(
          notebook.id,
          cellId,
          cell.content,
          cell.type
        );

        // Update cell with results (normal execution format)
        setCells(prevCells => prevCells.map(c => {
          if (c.id === cellId) {
            return {
              ...c,
              isRunning: false,
              executionId: execResult.data.executionId,
              output: {
                text: execResult.data.output,
                figures: execResult.data.figures || [],
                error: execResult.data.error
              }
            };
          }
          return c;
        }));
      }

    } catch (error) {
      console.error('Error executing cell:', error);
      
      // Update cell with error
      setCells(prevCells => prevCells.map(c => {
        if (c.id === cellId) {
          return {
            ...c,
            isRunning: false,
            output: {
              text: '',
              figures: [],
              error: {
                type: 'ExecutionError',
                message: error instanceof Error ? error.message : 'Unknown error',
                traceback: error instanceof Error ? error.stack || '' : ''
              }
            }
          };
        }
        return c;
      }));
    }
  };

  const runAllCells = () => {
    setIsRunning(true);
    // Simulate running all cells
    setTimeout(() => {
      setIsRunning(false);
    }, 3000);
  };

  if (loadingNotebook) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading notebook...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo & Notebook Info */}
            <div className="flex items-center space-x-4">
              <Link href="/lab" className="flex items-center group">
                <motion.div
                  className="relative p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg mr-3"
                  whileHover={{ scale: 1.05, rotate: 5 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <Zap className="w-5 h-5 text-white" />
                </motion.div>
                <div>
                  <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    EnsimuNotebook
                  </span>
                </div>
              </Link>
              
              <div className="hidden md:block">
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {notebook?.name || 'Untitled Notebook'}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {notebook?.description || 'No description'}
                </div>
              </div>
            </div>

            {/* Toolbar */}
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={runAllCells}
                disabled={isRunning}
              >
                <Play className="w-4 h-4 mr-2" />
                {isRunning ? 'Running...' : 'Run All'}
              </Button>
              
              <Button variant="outline" size="sm">
                <Save className="w-4 h-4 mr-2" />
                Save
              </Button>

              <Button variant="outline" size="sm">
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </Button>

              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setAiSidebarOpen(true)}
                className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200 text-purple-700 hover:from-purple-100 hover:to-blue-100"
              >
                <Bot className="w-4 h-4 mr-2" />
                AI Assistant
              </Button>

              <div className="relative group">
                <Button variant="outline" size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Cell
                  <ChevronDown className="w-3 h-3 ml-1" />
                </Button>
                
                <div className="absolute right-0 top-full mt-1 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                  <button
                    onClick={() => addCell('code')}
                    className="w-full flex items-center space-x-3 px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <Code className="w-4 h-4" />
                    <span>Code Cell</span>
                  </button>
                  <button
                    onClick={() => addCell('markdown')}
                    className="w-full flex items-center space-x-3 px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <FileText className="w-4 h-4" />
                    <span>Markdown Cell</span>
                  </button>
                  <button
                    onClick={() => addCell('physics')}
                    className="w-full flex items-center space-x-3 px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <Zap className="w-4 h-4" />
                    <span>Physics Cell</span>
                  </button>
                </div>
              </div>

              <UserMenu />
            </div>
          </div>
        </div>
      </header>

      {/* Notebook Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-4">
          {cells.map((cell, index) => (
            <motion.div
              key={cell.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <CellComponent
                cell={cell}
                onUpdate={(content) => updateCell(cell.id, content)}
                onDelete={() => deleteCell(cell.id)}
                onRun={() => runCell(cell.id)}
                onAddCell={(type) => addCell(type, index)}
                onFocus={() => setCurrentCell(cell)}
              />
            </motion.div>
          ))}
        </div>

        {/* Add Cell Button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: cells.length * 0.1 }}
          className="mt-8 text-center"
        >
          <Button
            variant="outline"
            onClick={() => addCell('code')}
            className="border-dashed border-2"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Cell
          </Button>
        </motion.div>
      </div>

      {/* AI Assistant Sidebar */}
      <AIAssistantSidebar
        isOpen={aiSidebarOpen}
        onClose={() => setAiSidebarOpen(false)}
        currentCellContent={currentCell?.content || ''}
        currentCellType={currentCell?.type || 'code'}
        onInsertCode={(code) => {
          console.log('Inserting code:', code);
          console.log('Current cell:', currentCell);
          if (currentCell) {
            const newContent = currentCell.content + '\n\n' + code;
            console.log('New content:', newContent);
            updateCell(currentCell.id, newContent);
          } else {
            // Create new cell if no current cell
            const newCellId = Date.now().toString();
            const newCell: Cell = {
              id: newCellId,
              type: 'code',
              content: code,
            };
            setCells(prev => [...prev, newCell]);
          }
        }}
      />
    </div>
  );
}