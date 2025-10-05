const express = require('express');
const router = express.Router();
const AICodeAnalysisService = require('../services/aiCodeAnalysis');
const logger = require('../utils/logger');

const aiCodeAnalysis = new AICodeAnalysisService();

/**
 * @route POST /api/ai/chat
 * @desc AI Chat endpoint for simulation assistance
 */
router.post('/chat', async (req, res) => {
  try {
    const { message, notebookContext, conversationHistory } = req.body;

    logger.info('🤖 AI Chat request:', {
      messageLength: message?.length,
      hasContext: !!notebookContext,
      historyLength: conversationHistory?.length || 0
    });

    // Analyze the user's message and notebook context
    const analysisResult = await analyzeUserRequest(message, notebookContext, conversationHistory);

    res.json({
      success: true,
      response: analysisResult.response,
      type: analysisResult.type,
      codeBlock: analysisResult.codeBlock,
      suggestions: analysisResult.suggestions
    });

  } catch (error) {
    logger.error('AI Chat error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process AI chat request'
    });
  }
});

/**
 * @route POST /api/ai/analyze-code
 * @desc Analyze code for performance, quality, and best practices
 */
router.post('/analyze-code', async (req, res) => {
    try {
        const { code, context } = req.body;

        if (!code) {
            return res.status(400).json({
                success: false,
                error: 'Code is required for analysis'
            });
        }

        console.log('🔬 AI Code Analysis Request:', {
            codeLength: code.length,
            hasContext: !!context,
            timestamp: new Date().toISOString()
        });

        const result = await aiCodeAnalysis.analyzeCode(code, context);

        console.log('✅ AI Code Analysis Complete:', {
            success: result.success,
            hasAnalysis: !!result.analysis,
            hasFallback: !!result.fallback
        });

        res.json(result);
    } catch (error) {
        console.error('❌ AI Code Analysis Error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error during code analysis',
            message: error.message
        });
    }
});

/**
 * @route POST /api/ai/optimize-code
 * @desc Generate code optimization suggestions
 */
router.post('/optimize-code', async (req, res) => {
    try {
        const { code, optimizationType = 'all' } = req.body;

        if (!code) {
            return res.status(400).json({
                success: false,
                error: 'Code is required for optimization'
            });
        }

        console.log('⚡ AI Code Optimization Request:', {
            codeLength: code.length,
            optimizationType,
            timestamp: new Date().toISOString()
        });

        const result = await aiCodeAnalysis.optimizeCode(code, optimizationType);

        console.log('✅ AI Code Optimization Complete:', {
            success: result.success,
            optimizationCount: result.optimizations?.length || 0
        });

        res.json(result);
    } catch (error) {
        console.error('❌ AI Code Optimization Error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error during code optimization',
            message: error.message
        });
    }
});

/**
 * @route POST /api/ai/explain-code
 * @desc Explain code functionality and concepts
 */
router.post('/explain-code', async (req, res) => {
    try {
        const { code } = req.body;

        if (!code) {
            return res.status(400).json({
                success: false,
                error: 'Code is required for explanation'
            });
        }

        console.log('📚 AI Code Explanation Request:', {
            codeLength: code.length,
            timestamp: new Date().toISOString()
        });

        const result = await aiCodeAnalysis.explainCode(code);

        console.log('✅ AI Code Explanation Complete:', {
            success: result.success,
            hasExplanation: !!result.explanation
        });

        res.json(result);
    } catch (error) {
        console.error('❌ AI Code Explanation Error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error during code explanation',
            message: error.message
        });
    }
});

/**
 * @route POST /api/ai/detect-issues
 * @desc Detect potential bugs and security issues
 */
router.post('/detect-issues', async (req, res) => {
    try {
        const { code } = req.body;

        if (!code) {
            return res.status(400).json({
                success: false,
                error: 'Code is required for issue detection'
            });
        }

        console.log('🔍 AI Issue Detection Request:', {
            codeLength: code.length,
            timestamp: new Date().toISOString()
        });

        const result = await aiCodeAnalysis.detectIssues(code);

        console.log('✅ AI Issue Detection Complete:', {
            success: result.success,
            issueCount: result.issues?.length || 0
        });

        res.json(result);
    } catch (error) {
        console.error('❌ AI Issue Detection Error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error during issue detection',
            message: error.message
        });
    }
});

/**
 * @route POST /api/ai/generate-tests
 * @desc Generate unit tests for the code
 */
router.post('/generate-tests', async (req, res) => {
    try {
        const { code } = req.body;

        if (!code) {
            return res.status(400).json({
                success: false,
                error: 'Code is required for test generation'
            });
        }

        console.log('🧪 AI Test Generation Request:', {
            codeLength: code.length,
            timestamp: new Date().toISOString()
        });

        const result = await aiCodeAnalysis.generateTests(code);

        console.log('✅ AI Test Generation Complete:', {
            success: result.success,
            hasTests: !!result.tests
        });

        res.json(result);
    } catch (error) {
        console.error('❌ AI Test Generation Error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error during test generation',
            message: error.message
        });
    }
});

/**
 * @route GET /api/ai/features
 * @desc Get available AI code analysis features
 */
router.get('/features', (req, res) => {
    res.json({
        success: true,
        features: [
            {
                id: 'chat',
                name: 'AI Chat Assistant',
                description: 'Interactive chat for simulation assistance, code generation, and debugging',
                endpoint: '/api/ai/chat',
                methods: ['POST']
            },
            {
                id: 'analyze-code',
                name: 'Code Analysis',
                description: 'Comprehensive code quality analysis with metrics and suggestions',
                endpoint: '/api/ai/analyze-code',
                methods: ['POST']
            },
            {
                id: 'optimize-code',
                name: 'Code Optimization',
                description: 'Performance and quality optimization suggestions',
                endpoint: '/api/ai/optimize-code',
                methods: ['POST'],
                parameters: ['optimizationType: performance|memory|quality|all']
            },
            {
                id: 'explain-code',
                name: 'Code Explanation',
                description: 'Detailed code explanation with concepts and algorithms',
                endpoint: '/api/ai/explain-code',
                methods: ['POST']
            },
            {
                id: 'detect-issues',
                name: 'Issue Detection',
                description: 'Bug and security issue detection with suggestions',
                endpoint: '/api/ai/detect-issues',
                methods: ['POST']
            },
            {
                id: 'generate-tests',
                name: 'Test Generation',
                description: 'Automated unit test generation for functions',
                endpoint: '/api/ai/generate-tests',
                methods: ['POST']
            }
        ],
        version: '1.0.0',
        status: 'active'
    });
});

// Helper functions for AI chat
async function analyzeUserRequest(message, notebookContext, conversationHistory) {
  const lowercaseMessage = message.toLowerCase();
  
  // Check for code generation requests
  if (lowercaseMessage.includes('write') || lowercaseMessage.includes('code') || lowercaseMessage.includes('simulation')) {
    return generateCodeSuggestion(message, notebookContext);
  }
  
  // Check for debugging requests
  if (lowercaseMessage.includes('debug') || lowercaseMessage.includes('error') || lowercaseMessage.includes('fix')) {
    return debugAssistance(message, notebookContext);
  }
  
  // Check for improvement suggestions
  if (lowercaseMessage.includes('improve') || lowercaseMessage.includes('optimize') || lowercaseMessage.includes('better')) {
    return improvementSuggestions(message, notebookContext);
  }
  
  // Check for 3D visualization requests
  if (lowercaseMessage.includes('3d') || lowercaseMessage.includes('visualization') || lowercaseMessage.includes('plot')) {
    return generate3DVisualization(message, notebookContext);
  }
  
  // Check for physics/engineering concepts
  if (lowercaseMessage.includes('physics') || lowercaseMessage.includes('engineering') || lowercaseMessage.includes('explain')) {
    return explainConcepts(message, notebookContext);
  }
  
  // General assistance
  return generateGeneralResponse(message, notebookContext);
}

function generateCodeSuggestion(message, notebookContext) {
  const codeExamples = {
    'fluid dynamics': `# External Flow Around Sphere - CFD Simulation
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as patches

# Simulation parameters
D = 1.0  # Sphere diameter (m)
R = D / 2  # Sphere radius (m)
U_inf = 10.0  # Free stream velocity (m/s)
rho = 1.225  # Air density (kg/m³)
mu = 1.789e-5  # Dynamic viscosity (Pa⋅s)
Re = rho * U_inf * D / mu  # Reynolds number

print(f"🌀 External Flow Around Sphere Analysis")
print(f"Reynolds Number: Re = {Re:.0f}")

# Create computational domain
x_domain = np.linspace(-3*R, 6*R, 100)
y_domain = np.linspace(-3*R, 3*R, 80)
X, Y = np.meshgrid(x_domain, y_domain)

# Distance from sphere center
r = np.sqrt(X**2 + Y**2)

# Potential flow solution around sphere (inviscid)
# Stream function: ψ = U_inf * y * (1 - R²/r²)
# Velocity potential: φ = U_inf * x * (1 + R²/(2*r²))

# Velocity components (potential flow)
u_potential = U_inf * (1 + (R**2 / (2 * r**2)) * (1 - 2*X**2/r**2))
v_potential = -U_inf * (R**2 / (2 * r**2)) * (2*X*Y/r**2)

# Mask for inside sphere
sphere_mask = r <= R
u_potential[sphere_mask] = 0
v_potential[sphere_mask] = 0

# Pressure coefficient (Cp) using Bernoulli's equation
# Cp = 1 - (V/U_inf)²
V_mag = np.sqrt(u_potential**2 + v_potential**2)
V_mag[sphere_mask] = 0
Cp = 1 - (V_mag / U_inf)**2

# Angle around sphere surface for pressure analysis
theta = np.linspace(0, np.pi, 100)  # 0 to π (front to back)
x_surface = R * np.cos(theta)
y_surface = R * np.sin(theta)

# Theoretical pressure coefficient on sphere surface
Cp_theory = 1 - (9/4) * np.sin(theta)**2

# Create comprehensive visualization
fig = plt.figure(figsize=(16, 12))

# Plot 1: Streamlines and pressure field
ax1 = fig.add_subplot(2, 3, 1)
# Pressure contour
pressure_contour = ax1.contourf(X, Y, Cp, levels=20, cmap='RdBu_r', alpha=0.7)
plt.colorbar(pressure_contour, ax=ax1, label='Pressure Coefficient (Cp)')

# Streamlines
ax1.streamplot(X, Y, u_potential, v_potential, density=2, color='black', linewidth=0.8)

# Draw sphere
circle = patches.Circle((0, 0), R, facecolor='gray', edgecolor='black', alpha=0.8)
ax1.add_patch(circle)

ax1.set_xlim(-3*R, 6*R)
ax1.set_ylim(-3*R, 3*R)
ax1.set_xlabel('x/D')
ax1.set_ylabel('y/D')
ax1.set_title(f'Flow Field Around Sphere (Re = {Re:.0f})')
ax1.set_aspect('equal')

# Plot 2: Velocity magnitude
ax2 = fig.add_subplot(2, 3, 2)
velocity_contour = ax2.contourf(X, Y, V_mag/U_inf, levels=20, cmap='viridis')
plt.colorbar(velocity_contour, ax=ax2, label='V/U∞')
circle2 = patches.Circle((0, 0), R, facecolor='white', edgecolor='black')
ax2.add_patch(circle2)
ax2.set_title('Velocity Magnitude')
ax2.set_xlabel('x/D')
ax2.set_ylabel('y/D')
ax2.set_aspect('equal')

# Plot 3: Pressure distribution on sphere surface
ax3 = fig.add_subplot(2, 3, 3)
ax3.plot(theta*180/np.pi, Cp_theory, 'b-', linewidth=2, label='Potential Flow Theory')
ax3.set_xlabel('Angle from stagnation point (degrees)')
ax3.set_ylabel('Pressure Coefficient (Cp)')
ax3.set_title('Surface Pressure Distribution')
ax3.grid(True)
ax3.legend()
ax3.set_xlim(0, 180)

# Plot 4: 3D velocity field
ax4 = fig.add_subplot(2, 3, 4, projection='3d')
# Sample the velocity field for 3D visualization
x_3d = X[::8, ::8]
y_3d = Y[::8, ::8]
z_3d = np.zeros_like(x_3d)
u_3d = u_potential[::8, ::8]
v_3d = v_potential[::8, ::8]
w_3d = np.zeros_like(u_3d)

# Remove vectors inside sphere
r_3d = np.sqrt(x_3d**2 + y_3d**2)
mask_3d = r_3d > R

ax4.quiver(x_3d[mask_3d], y_3d[mask_3d], z_3d[mask_3d], 
          u_3d[mask_3d], v_3d[mask_3d], w_3d[mask_3d], 
          length=0.3, alpha=0.6, color='blue')

# Draw sphere in 3D
u_sphere = np.linspace(0, 2 * np.pi, 20)
v_sphere = np.linspace(0, np.pi, 20)
x_sphere = R * np.outer(np.cos(u_sphere), np.sin(v_sphere))
y_sphere = R * np.outer(np.sin(u_sphere), np.sin(v_sphere))
z_sphere = R * np.outer(np.ones(np.size(u_sphere)), np.cos(v_sphere))
ax4.plot_surface(x_sphere, y_sphere, z_sphere, alpha=0.3, color='gray')

ax4.set_title('3D Velocity Vectors')
ax4.set_xlabel('X')
ax4.set_ylabel('Y')
ax4.set_zlabel('Z')

# Plot 5: Drag coefficient analysis
ax5 = fig.add_subplot(2, 3, 5)
Re_range = np.logspace(0, 6, 100)

# Drag coefficient correlations for different Re ranges
def drag_coefficient(Re):
    if Re < 1:
        return 24/Re  # Stokes flow
    elif Re < 1000:
        return 24/Re * (1 + 0.15*Re**0.687)  # Intermediate
    elif Re < 200000:
        return 0.44  # Newton's regime
    else:
        return 0.1  # Turbulent

Cd_values = [drag_coefficient(re) for re in Re_range]

ax5.loglog(Re_range, Cd_values, 'b-', linewidth=2, label='Drag Correlation')
ax5.axvline(Re, color='red', linestyle='--', label=f'Current Re = {Re:.0f}')
ax5.set_xlabel('Reynolds Number (Re)')
ax5.set_ylabel('Drag Coefficient (Cd)')
ax5.set_title('Drag Coefficient vs Reynolds Number')
ax5.grid(True, alpha=0.3)
ax5.legend()

# Plot 6: Engineering results summary
ax6 = fig.add_subplot(2, 3, 6)
ax6.axis('off')

# Calculate engineering parameters
Cd_current = drag_coefficient(Re)
drag_force = 0.5 * rho * U_inf**2 * (np.pi * R**2) * Cd_current
wake_length = 2.5 * D if Re > 40 else 0

results_text = f"""
FLOW ANALYSIS RESULTS
=====================
Reynolds Number: {Re:.0f}
Flow Regime: {"Laminar" if Re < 200000 else "Turbulent"}

SPHERE PARAMETERS:
Diameter: {D:.1f} m
Frontal Area: {np.pi * R**2:.3f} m²

FLUID PROPERTIES:
Velocity: {U_inf:.1f} m/s
Density: {rho:.3f} kg/m³
Viscosity: {mu:.2e} Pa⋅s

RESULTS:
Drag Coefficient: {Cd_current:.3f}
Drag Force: {drag_force:.1f} N
Wake Length: {wake_length:.1f} m

STAGNATION POINT:
Pressure: {0.5 * rho * U_inf**2:.1f} Pa
Cp_max: 1.000

SEPARATION POINT:
Angle: ~80-120° (Re dependent)
"""

ax6.text(0.05, 0.95, results_text, transform=ax6.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

plt.tight_layout()
plt.show()

print("🌊 Flow simulation complete!")
print(f"💨 Drag force: {drag_force:.1f} N")
print(f"📊 Pressure recovery in wake region")
print(f"🎯 Use results for aerodynamic design optimization")`,

    'heat transfer': `# Heat Transfer Simulation
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Parameters
L = 1.0  # Length (m)
W = 1.0  # Width (m)
alpha = 1e-4  # Thermal diffusivity (m²/s)
T_initial = 20  # Initial temperature (°C)
T_boundary = 100  # Boundary temperature (°C)

# Create mesh
nx, ny = 50, 50
x = np.linspace(0, L, nx)
y = np.linspace(0, W, ny)
X, Y = np.meshgrid(x, y)

# Initial temperature distribution
T = np.ones((nx, ny)) * T_initial
T[0, :] = T_boundary  # Top boundary
T[-1, :] = T_boundary  # Bottom boundary
T[:, 0] = T_boundary  # Left boundary
T[:, -1] = T_boundary  # Right boundary

# Plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(X, Y, T, cmap='hot')
ax.set_title('Heat Distribution')
plt.colorbar(surf)
plt.show()

print("🔥 Heat transfer simulation ready!")`,

    'beam analysis': `# Structural Beam Analysis
import numpy as np
import matplotlib.pyplot as plt

# Beam parameters
L = 10.0  # Length (m)
E = 200e9  # Young's modulus (Pa) - Steel
I = 8.3e-6  # Second moment of area (m^4)
w = 5000  # Distributed load (N/m)

# Position along beam
x = np.linspace(0, L, 100)

# Deflection equation for simply supported beam with uniform load
def deflection(x, L, w, E, I):
    return (w * x / (24 * E * I)) * (L**3 - 2*L*x**2 + x**3)

# Calculate deflection
y = deflection(x, L, w, E, I)

# Maximum values
max_deflection = np.max(np.abs(y))
max_moment = w * L**2 / 8
max_stress = max_moment * 0.05 / I  # Assuming c = 0.05m

# Plot
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(x, y*1000, 'b-', linewidth=2)
plt.xlabel('Position (m)')
plt.ylabel('Deflection (mm)')
plt.title('Beam Deflection')
plt.grid(True)

plt.subplot(1, 2, 2)
moment = w * x * (L - x) / 2
plt.plot(x, moment/1000, 'r-', linewidth=2)
plt.xlabel('Position (m)')
plt.ylabel('Moment (kN⋅m)')
plt.title('Bending Moment')
plt.grid(True)

plt.tight_layout()
plt.show()

print(f"📊 Max deflection: {max_deflection*1000:.2f} mm")
print(f"📊 Max stress: {max_stress/1e6:.1f} MPa")`,

    '3d visualization': `# Advanced 3D Visualization
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Generate sample 3D data
def create_3d_field():
    x = np.linspace(-2, 2, 30)
    y = np.linspace(-2, 2, 30) 
    z = np.linspace(-1, 1, 20)
    X, Y, Z = np.meshgrid(x, y, z)
    
    # Example: 3D Gaussian field
    field = np.exp(-(X**2 + Y**2 + Z**2))
    return X, Y, Z, field

X, Y, Z, field = create_3d_field()

# Create 3D visualization
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot points where field > threshold
mask = field > 0.1
scatter = ax.scatter(X[mask], Y[mask], Z[mask], 
                    c=field[mask], cmap='plasma', s=20, alpha=0.6)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Field Visualization')
plt.colorbar(scatter)
plt.show()

print("📊 3D visualization created!")`
  };

  // Determine which example to suggest based on message content
  let suggestedCode = '';
  let description = '';
  
  if (message.toLowerCase().includes('fluid') || message.toLowerCase().includes('flow') || message.toLowerCase().includes('sphere')) {
    suggestedCode = codeExamples['fluid dynamics'];
    description = "Here's a comprehensive fluid dynamics simulation for external flow around a sphere. This includes flow field analysis, pressure distribution, drag coefficient calculation, and detailed engineering results.";
  } else if (message.toLowerCase().includes('heat')) {
    suggestedCode = codeExamples['heat transfer'];
    description = "Here's a heat transfer simulation that creates a 3D temperature distribution plot.";
  } else if (message.toLowerCase().includes('beam') || message.toLowerCase().includes('structural')) {
    suggestedCode = codeExamples['beam analysis'];
    description = "Here's a structural beam analysis that calculates deflection and bending moments.";
  } else if (message.toLowerCase().includes('3d') || message.toLowerCase().includes('visualization')) {
    suggestedCode = codeExamples['3d visualization'];
    description = "Here's an advanced 3D visualization example for engineering data.";
  } else {
    // Default general simulation
    suggestedCode = `# General Engineering Simulation Template
import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
time = np.linspace(0, 10, 100)
amplitude = 5
frequency = 1

# Generate sample data
signal = amplitude * np.sin(2 * np.pi * frequency * time)

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(time, signal, 'b-', linewidth=2)
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.title('Engineering Simulation Results')
plt.grid(True)
plt.show()

print("✅ Simulation template ready - customize for your needs!")`;
    description = "Here's a general simulation template you can customize for your specific engineering application.";
  }

  return {
    response: `${description}\n\nClick the "Insert" button below to add this code to your notebook.`,
    type: 'code',
    codeBlock: suggestedCode
  };
}

function debugAssistance(message, notebookContext) {
  const cells = notebookContext?.cells || [];
  
  let debugResponse = "I'd be happy to help debug your code! ";
  
  if (cells.length === 0) {
    debugResponse += "I don't see any code in your notebook yet. Please share the code you're having trouble with.";
  } else {
    debugResponse += "Based on your notebook, here are some common debugging tips:\n\n";
    debugResponse += "🔍 **Common Issues to Check:**\n";
    debugResponse += "• Import statements - make sure all libraries are installed\n";
    debugResponse += "• Variable names - check for typos and case sensitivity\n";
    debugResponse += "• Array dimensions - ensure shapes match for operations\n";
    debugResponse += "• Missing parentheses or indentation errors\n\n";
    debugResponse += "💡 **Pro Tip:** Use `print()` statements to debug variable values and `plt.show()` to display plots.";
  }
  
  return {
    response: debugResponse,
    type: 'text',
    suggestions: [
      "Add debug print statements",
      "Check variable types with type()",
      "Verify array shapes with .shape",
      "Test with smaller datasets first"
    ]
  };
}

function improvementSuggestions(message, notebookContext) {
  const suggestions = [
    "🚀 **Performance:** Use vectorized NumPy operations instead of loops",
    "📊 **Visualization:** Add interactive plots with Plotly for better user experience", 
    "🔢 **Accuracy:** Increase mesh resolution for more precise results",
    "⚡ **Optimization:** Consider using compiled libraries like Numba for speed",
    "📝 **Documentation:** Add docstrings and comments to explain physics"
  ];
  
  return {
    response: "Here are some ways to improve your simulation:\n\n" + suggestions.join("\n\n") + 
             "\n\nWould you like me to help implement any of these improvements?",
    type: 'text'
  };
}

function generate3DVisualization(message, notebookContext) {
  const code3D = `# Advanced 3D Visualization
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Generate 3D engineering data
x = np.linspace(-5, 5, 25)
y = np.linspace(-5, 5, 25)
z = np.linspace(0, 10, 15)
X, Y, Z = np.meshgrid(x, y, z)

# Example: 3D scalar field (e.g., stress, temperature, pressure)
field = np.exp(-(X**2 + Y**2)/20) * np.sin(Z/2)

# Create multiple 3D visualizations
fig = plt.figure(figsize=(15, 5))

# 3D Scatter plot
ax1 = fig.add_subplot(131, projection='3d')
mask = field > 0.3
scatter = ax1.scatter(X[mask], Y[mask], Z[mask], 
                     c=field[mask], cmap='viridis', s=30, alpha=0.7)
ax1.set_title('3D Scatter Plot')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')

# 3D Surface plot (slice at z=5)
ax2 = fig.add_subplot(132, projection='3d')
z_slice = 7  # Choose slice index
surf = ax2.plot_surface(X[:,:,z_slice], Y[:,:,z_slice], 
                       field[:,:,z_slice], cmap='plasma', alpha=0.8)
ax2.set_title('Surface at Z=5')

# 3D Wireframe
ax3 = fig.add_subplot(133, projection='3d')
wire = ax3.plot_wireframe(X[:,:,z_slice], Y[:,:,z_slice], 
                         field[:,:,z_slice], alpha=0.6)
ax3.set_title('Wireframe View')

plt.tight_layout()
plt.show()

print("📊 3D visualizations created!")
print("💡 Adjust the field calculation for your specific data")`;

  return {
    response: "Here's an advanced 3D visualization example with multiple techniques:\n\n• **Scatter plots** for point clouds\n• **Surface plots** for continuous fields\n• **Wireframe plots** for structure visualization\n\nThis gives you several options depending on your data type and visualization needs.",
    type: 'code', 
    codeBlock: code3D
  };
}

function explainConcepts(message, notebookContext) {
  const concepts = {
    "heat transfer": "Heat transfer involves conduction, convection, and radiation. The heat equation ∂T/∂t = α∇²T governs temperature distribution over time.",
    "structural analysis": "Structural analysis uses stress (σ = F/A), strain (ε = ΔL/L), and Young's modulus (E = σ/ε) relationships.",
    "fluid dynamics": "Fluid dynamics is governed by the Navier-Stokes equations describing momentum conservation.",
    "vibration": "Vibration analysis studies oscillatory motion with natural frequency ωₙ = √(k/m) and damping."
  };
  
  let explanation = "I'd be happy to explain engineering concepts! ";
  let foundConcept = false;
  
  for (const [concept, description] of Object.entries(concepts)) {
    if (message.toLowerCase().includes(concept.replace(' ', ''))) {
      explanation += `\n\n📚 **${concept.toUpperCase()}**\n${description}`;
      foundConcept = true;
      break;
    }
  }
  
  if (!foundConcept) {
    explanation += "What specific physics or engineering concept would you like me to explain?";
  }
  
  return {
    response: explanation,
    type: 'text'
  };
}

function generateGeneralResponse(message, notebookContext) {
  return {
    response: "I'm here to help with your engineering simulations! I can:\n\n• Write Python code for simulations\n• Create 3D visualizations\n• Debug existing code\n• Explain physics concepts\n• Suggest improvements\n\n💡 Try asking me to help with a specific simulation type!",
    type: 'text'
  };
}

module.exports = router;