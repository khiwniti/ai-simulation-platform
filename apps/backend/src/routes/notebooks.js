const express = require('express');
const { v4: uuidv4 } = require('uuid');
const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const router = express.Router();
const logger = require('../utils/logger');

// Temporary in-memory storage for notebooks (replace with database later)
const notebooks = new Map();
const executions = new Map();

// Create a new notebook
router.post('/', async (req, res) => {
  try {
    const { name, description, template, type } = req.body;
    
    const notebookId = uuidv4();
    const notebook = {
      id: notebookId,
      name: name || 'Untitled Notebook',
      description: description || '',
      template: template || 'blank',
      type: type || 'general',
      cells: [],
      createdAt: new Date().toISOString(),
      lastModified: new Date().toISOString(),
      metadata: {
        kernel: 'python3',
        language: 'python'
      }
    };
    
    notebooks.set(notebookId, notebook);
    
    res.status(201).json({
      success: true,
      data: notebook
    });
  } catch (error) {
    logger.error('Error creating notebook:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create notebook'
    });
  }
});

// Get notebook by ID
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const notebook = notebooks.get(id);
    
    if (!notebook) {
      return res.status(404).json({
        success: false,
        error: 'Notebook not found'
      });
    }
    
    res.json({
      success: true,
      data: notebook
    });
  } catch (error) {
    logger.error('Error fetching notebook:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch notebook'
    });
  }
});

// Update notebook
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    
    const notebook = notebooks.get(id);
    if (!notebook) {
      return res.status(404).json({
        success: false,
        error: 'Notebook not found'
      });
    }
    
    const updatedNotebook = {
      ...notebook,
      ...updates,
      lastModified: new Date().toISOString()
    };
    
    notebooks.set(id, updatedNotebook);
    
    res.json({
      success: true,
      data: updatedNotebook
    });
  } catch (error) {
    logger.error('Error updating notebook:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update notebook'
    });
  }
});

// Execute code cell
router.post('/:id/execute', async (req, res) => {
  try {
    const { id } = req.params;
    const { cellId, code, cellType } = req.body;
    
    if (!code || code.trim() === '') {
      return res.json({
        success: true,
        data: {
          cellId,
          output: '',
          status: 'success'
        }
      });
    }
    
    const executionId = uuidv4();
    
    // Store execution info
    executions.set(executionId, {
      id: executionId,
      notebookId: id,
      cellId,
      code,
      status: 'running',
      startTime: new Date().toISOString()
    });
    
    // Create temporary Python file
    const tempDir = path.join(__dirname, '../../temp');
    await fs.mkdir(tempDir, { recursive: true });
    const pythonFile = path.join(tempDir, `${executionId}.py`);
    
    // Beta simplified Python code for basic execution
    const enhancedCode = `
import sys
import io
import traceback
import json

# Try to import common packages, but don't fail if they're not available
available_packages = []
try:
    import numpy as np
    available_packages.append('numpy')
except ImportError:
    pass

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64
    available_packages.append('matplotlib')
    plotting_available = True
except ImportError:
    plotting_available = False

# Capture stdout
old_stdout = sys.stdout
sys.stdout = captured_output = io.StringIO()

# Prepare plot capture
figures = []

def save_figure():
    """Save current figure to base64 string if matplotlib is available"""
    if plotting_available and 'matplotlib' in available_packages:
        try:
            if plt.get_fignums():
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode()
                figures.append(img_str)
                plt.close()
        except Exception as e:
            print(f"Warning: Could not save figure: {e}")

# Override plt.show if matplotlib is available
if plotting_available:
    original_show = plt.show
    def custom_show(*args, **kwargs):
        save_figure()
    plt.show = custom_show

try:
    # Print available packages info
    if available_packages:
        print(f"📦 Available packages: {', '.join(available_packages)}")
    else:
        print("📦 Running with basic Python (no data science packages)")
    print("---")
    
    # Execute user code
${code.split('\n').map(line => `    ${line}`).join('\n')}
    
    # Save any remaining figures
    if plotting_available:
        save_figure()
    
    # Get output
    output = captured_output.getvalue()
    
    # Prepare result
    result = {
        "success": True,
        "output": output,
        "figures": figures,
        "available_packages": available_packages,
        "error": None
    }
    
except Exception as e:
    # Get error output
    error_output = captured_output.getvalue()
    error_trace = traceback.format_exc()
    
    result = {
        "success": False,
        "output": error_output,
        "figures": [],
        "available_packages": available_packages,
        "error": {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": error_trace
        }
    }

finally:
    # Restore stdout
    sys.stdout = old_stdout
    
# Print result as JSON
print(json.dumps(result))
`;
    
    await fs.writeFile(pythonFile, enhancedCode);
    
    // Execute Python code
    const python = spawn('python3', [pythonFile], {
      timeout: 30000, // 30 second timeout
      cwd: tempDir
    });
    
    let stdout = '';
    let stderr = '';
    
    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    python.on('close', async (code) => {
      try {
        // Clean up temp file
        await fs.unlink(pythonFile).catch(() => {});
        
        let result;
        
        if (code === 0 && stdout.trim()) {
          try {
            // Parse JSON result from Python
            const lastLine = stdout.trim().split('\n').pop();
            result = JSON.parse(lastLine);
          } catch (parseError) {
            result = {
              success: true,
              output: stdout.trim(),
              figures: [],
              error: null
            };
          }
        } else {
          result = {
            success: false,
            output: stderr || stdout || 'No output',
            figures: [],
            error: {
              type: 'ExecutionError',
              message: stderr || 'Code execution failed',
              traceback: stderr
            }
          };
        }
        
        // Update execution status
        const execution = executions.get(executionId);
        if (execution) {
          execution.status = result.success ? 'completed' : 'failed';
          execution.endTime = new Date().toISOString();
          execution.result = result;
        }
        
        res.json({
          success: true,
          data: {
            executionId,
            cellId,
            output: result.output,
            figures: result.figures,
            error: result.error,
            status: result.success ? 'success' : 'error'
          }
        });
        
      } catch (cleanupError) {
        logger.error('Error during cleanup:', cleanupError);
        res.status(500).json({
          success: false,
          error: 'Execution completed but cleanup failed'
        });
      }
    });
    
    python.on('error', async (error) => {
      logger.error('Python execution error:', error);
      
      // Clean up temp file
      await fs.unlink(pythonFile).catch(() => {});
      
      res.status(500).json({
        success: false,
        error: 'Failed to execute code: ' + error.message
      });
    });
    
  } catch (error) {
    logger.error('Error executing code:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to execute code'
    });
  }
});

// Beta: Simple execute endpoint without notebook ID
router.post('/execute', async (req, res) => {
  try {
    const { code } = req.body;

    if (!code || code.trim() === '') {
      return res.json({
        success: true,
        output: '',
        error: null,
        figures: [],
        available_packages: []
      });
    }

    logger.info('🔬 Beta code execution request:', {
      codeLength: code.length,
      timestamp: new Date().toISOString()
    });

    const executionId = uuidv4();
    
    // Create temporary Python file
    const tempDir = path.join(__dirname, '../../temp');
    await fs.mkdir(tempDir, { recursive: true });
    const pythonFile = path.join(tempDir, `${executionId}.py`);
    
    // Beta simplified Python code for basic execution
    const enhancedCode = `
import sys
import io
import traceback
import json

# Try to import common packages, but don't fail if they're not available
available_packages = []
try:
    import numpy as np
    available_packages.append('numpy')
except ImportError:
    pass

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64
    available_packages.append('matplotlib')
    plotting_available = True
except ImportError:
    plotting_available = False

# Capture stdout
old_stdout = sys.stdout
sys.stdout = captured_output = io.StringIO()

# Prepare plot capture
figures = []

def save_figure():
    """Save current figure to base64 string if matplotlib is available"""
    if plotting_available and 'matplotlib' in available_packages:
        try:
            if plt.get_fignums():
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode()
                figures.append(img_str)
                plt.close()
        except Exception as e:
            print(f"Warning: Could not save figure: {e}")

# Override plt.show if matplotlib is available
if plotting_available:
    original_show = plt.show
    def custom_show(*args, **kwargs):
        save_figure()
    plt.show = custom_show

try:
    # Print available packages info
    if available_packages:
        print(f"📦 Available packages: {', '.join(available_packages)}")
    else:
        print("📦 Running with basic Python (no data science packages)")
    print("---")
    
    # Execute user code
${code.split('\n').map(line => `    ${line}`).join('\n')}
    
    # Save any remaining figures
    if plotting_available:
        save_figure()
    
    # Get output
    output = captured_output.getvalue()
    
    # Prepare result
    result = {
        "success": True,
        "output": output,
        "figures": figures,
        "available_packages": available_packages,
        "error": None
    }
    
except Exception as e:
    # Get error output
    error_output = captured_output.getvalue()
    error_trace = traceback.format_exc()
    
    result = {
        "success": False,
        "output": error_output,
        "figures": [],
        "available_packages": available_packages,
        "error": {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": error_trace
        }
    }

finally:
    # Restore stdout
    sys.stdout = old_stdout
    
# Print result as JSON
print(json.dumps(result))
`;
    
    await fs.writeFile(pythonFile, enhancedCode);
    
    // Execute Python code
    const python = spawn('python3', [pythonFile], {
      timeout: 30000, // 30 second timeout
      encoding: 'utf8'
    });
    
    let stdout = '';
    let stderr = '';
    
    python.stdout.on('data', (data) => {
      stdout += data;
    });
    
    python.stderr.on('data', (data) => {
      stderr += data;
    });
    
    python.on('close', async (code) => {
      try {
        // Clean up temp file
        await fs.unlink(pythonFile).catch(() => {});
        
        let result;
        if (code === 0 && stdout.trim()) {
          try {
            // Try to parse the last line as JSON (our result)
            const lines = stdout.trim().split('\n');
            const lastLine = lines[lines.length - 1];
            result = JSON.parse(lastLine);
          } catch (parseError) {
            result = {
              success: true,
              output: stdout.trim(),
              figures: [],
              available_packages: [],
              error: null
            };
          }
        } else {
          result = {
            success: false,
            output: stderr || stdout || 'No output',
            figures: [],
            available_packages: [],
            error: {
              type: 'ExecutionError',
              message: stderr || 'Code execution failed',
              traceback: stderr
            }
          };
        }

        logger.info('✅ Beta code execution complete:', {
          success: result.success,
          hasOutput: !!result.output,
          hasError: !!result.error,
          figureCount: result.figures?.length || 0,
          packages: result.available_packages?.join(', ') || 'none'
        });

        res.json(result);
        
      } catch (cleanupError) {
        logger.error('Error during cleanup:', cleanupError);
        res.status(500).json({
          success: false,
          error: 'Execution completed but cleanup failed',
          output: '',
          figures: [],
          available_packages: []
        });
      }
    });
    
    python.on('error', async (error) => {
      logger.error('❌ Beta code execution error:', error);
      
      // Clean up temp file
      await fs.unlink(pythonFile).catch(() => {});
      
      res.status(500).json({
        success: false,
        error: 'Failed to execute code: ' + error.message,
        output: '',
        figures: [],
        available_packages: []
      });
    });

  } catch (error) {
    logger.error('❌ Beta code execution setup error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to execute code: ' + error.message,
      output: '',
      figures: [],
      available_packages: []
    });
  }
});

// Get execution status
router.get('/:id/executions/:executionId', async (req, res) => {
  try {
    const { executionId } = req.params;
    const execution = executions.get(executionId);
    
    if (!execution) {
      return res.status(404).json({
        success: false,
        error: 'Execution not found'
      });
    }
    
    res.json({
      success: true,
      data: execution
    });
  } catch (error) {
    logger.error('Error fetching execution:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch execution'
    });
  }
});

// List all notebooks (for dashboard)
router.get('/', async (req, res) => {
  try {
    const notebookList = Array.from(notebooks.values());
    
    res.json({
      success: true,
      data: notebookList
    });
  } catch (error) {
    logger.error('Error listing notebooks:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to list notebooks'
    });
  }
});

// Delete notebook
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    if (!notebooks.has(id)) {
      return res.status(404).json({
        success: false,
        error: 'Notebook not found'
      });
    }
    
    notebooks.delete(id);
    
    res.json({
      success: true,
      message: 'Notebook deleted successfully'
    });
  } catch (error) {
    logger.error('Error deleting notebook:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete notebook'
    });
  }
});

module.exports = router;