"""
Physics-aware Python code execution script with NVIDIA PhysX AI support
"""

import sys
import json
import traceback
import io
import base64
import os
from contextlib import redirect_stdout, redirect_stderr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


class PhysXAIWrapper:
    """
    Wrapper for NVIDIA PhysX AI functionality
    In a real implementation, this would interface with actual PhysX AI libraries
    """
    
    def __init__(self):
        self.is_available = self._check_availability()
        self.gpu_device = os.environ.get('CUDA_VISIBLE_DEVICES', '')
        self.memory_limit = int(os.environ.get('PHYSX_GPU_MEMORY_MB', '512'))
        
    def _check_availability(self) -> bool:
        """Check if PhysX AI is available"""
        try:
            # In real implementation, this would check for PhysX AI libraries
            physx_enabled = os.environ.get('PHYSX_AI_ENABLED', '0') == '1'
            gpu_available = os.environ.get('CUDA_VISIBLE_DEVICES', '') != ''
            return physx_enabled and gpu_available
        except Exception:
            return False
            
    def initialize_physics_context(self):
        """Initialize PhysX AI physics context"""
        if not self.is_available:
            return False
            
        try:
            # In real implementation, this would initialize PhysX AI
            print(f"PhysX AI initialized on GPU {self.gpu_device} with {self.memory_limit}MB")
            return True
        except Exception as e:
            print(f"PhysX AI initialization failed: {e}")
            return False
            
    def create_physics_simulation(self, params: dict):
        """Create a physics simulation using PhysX AI"""
        if not self.is_available:
            raise RuntimeError("PhysX AI not available")
            
        # Placeholder for actual PhysX AI simulation creation
        return {
            "simulation_id": "physx_sim_001",
            "engine": "PhysX AI",
            "gpu_device": self.gpu_device,
            "parameters": params
        }


class PhysXCPUWrapper:
    """
    Wrapper for NVIDIA PhysX CPU functionality
    """
    
    def __init__(self):
        self.is_available = self._check_availability()
        self.thread_count = int(os.environ.get('PHYSX_CPU_THREADS', '4'))
        
    def _check_availability(self) -> bool:
        """Check if PhysX CPU is available"""
        return os.environ.get('PHYSX_CPU_ENABLED', '0') == '1'
        
    def initialize_physics_context(self):
        """Initialize PhysX CPU physics context"""
        if not self.is_available:
            return False
            
        try:
            print(f"PhysX CPU initialized with {self.thread_count} threads")
            return True
        except Exception as e:
            print(f"PhysX CPU initialization failed: {e}")
            return False
            
    def create_physics_simulation(self, params: dict):
        """Create a physics simulation using PhysX CPU"""
        if not self.is_available:
            raise RuntimeError("PhysX CPU not available")
            
        return {
            "simulation_id": "physx_cpu_sim_001",
            "engine": "PhysX CPU",
            "threads": self.thread_count,
            "parameters": params
        }


class SoftwareFallbackPhysics:
    """
    Software fallback physics implementation using standard libraries
    """
    
    def __init__(self):
        self.is_available = True
        
    def initialize_physics_context(self):
        """Initialize software physics context"""
        print("Software physics fallback initialized")
        return True
        
    def create_physics_simulation(self, params: dict):
        """Create a physics simulation using software fallback"""
        return {
            "simulation_id": "software_sim_001",
            "engine": "Software Fallback",
            "parameters": params
        }


def setup_physics_environment():
    """Set up the physics environment based on available engines"""
    physics_engine = os.environ.get('PHYSICS_ENGINE', 'software_fallback')
    
    if physics_engine == 'physx_ai':
        wrapper = PhysXAIWrapper()
        if wrapper.initialize_physics_context():
            return wrapper
        else:
            print("Falling back to PhysX CPU")
            physics_engine = 'physx_cpu'
    
    if physics_engine == 'physx_cpu':
        wrapper = PhysXCPUWrapper()
        if wrapper.initialize_physics_context():
            return wrapper
        else:
            print("Falling back to software physics")
            physics_engine = 'software_fallback'
    
    # Software fallback
    wrapper = SoftwareFallbackPhysics()
    wrapper.initialize_physics_context()
    return wrapper


def inject_physics_globals(exec_globals: dict, physics_wrapper):
    """Inject physics-related globals into execution environment"""
    
    # Physics simulation creation function
    def create_physics_sim(**params):
        """Create a physics simulation with the available engine"""
        return physics_wrapper.create_physics_simulation(params)
    
    # Physics utilities
    def get_physics_info():
        """Get information about the physics environment"""
        return {
            "engine": os.environ.get('PHYSICS_ENGINE', 'software_fallback'),
            "gpu_device": os.environ.get('CUDA_VISIBLE_DEVICES', 'none'),
            "memory_limit": os.environ.get('PHYSX_GPU_MEMORY_MB', 'none'),
            "simulation_id": os.environ.get('SIMULATION_ID', 'unknown')
        }
    
    # Simple physics simulation example using numpy
    def simulate_particle_system(particles, forces, dt=0.01, steps=100):
        """Simple particle system simulation"""
        positions = np.array(particles['positions'])
        velocities = np.array(particles['velocities'])
        masses = np.array(particles['masses'])
        
        trajectory = []
        
        for step in range(steps):
            # Apply forces
            accelerations = np.array(forces) / masses.reshape(-1, 1)
            
            # Update velocities and positions
            velocities += accelerations * dt
            positions += velocities * dt
            
            trajectory.append(positions.copy())
            
        return np.array(trajectory)
    
    # Inject into globals
    exec_globals.update({
        'create_physics_sim': create_physics_sim,
        'get_physics_info': get_physics_info,
        'simulate_particle_system': simulate_particle_system,
        'np': np,  # Ensure numpy is available
    })


def capture_output():
    """Main execution function with physics support"""
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    
    # Set up physics environment
    physics_wrapper = setup_physics_environment()
    
    try:
        # Read user code from stdin
        user_code = sys.stdin.read()
        
        # Redirect stdout and stderr
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            # Execute user code with physics support
            exec_globals = {'__name__': '__main__'}
            inject_physics_globals(exec_globals, physics_wrapper)
            
            exec(user_code, exec_globals)
            
        # Capture any matplotlib figures
        figures = []
        for i in plt.get_fignums():
            fig = plt.figure(i)
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
            img_buffer.seek(0)
            img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            figures.append(img_data)
            plt.close(fig)
            
        # Output results
        stdout_content = stdout_buffer.getvalue()
        if stdout_content:
            print(json.dumps({
                "output_type": "stdout",
                "content": {"text": stdout_content},
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            }))
            
        # Output figures
        for i, fig_data in enumerate(figures):
            print(json.dumps({
                "output_type": "display_data",
                "content": {
                    "data": {
                        "image/png": fig_data
                    },
                    "metadata": {}
                },
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            }))
            
    except Exception as e:
        # Output error
        error_traceback = traceback.format_exc()
        print(json.dumps({
            "output_type": "error",
            "content": {
                "ename": type(e).__name__,
                "evalue": str(e),
                "traceback": error_traceback.split('\n')
            },
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }))
        
    # Output stderr if any
    stderr_content = stderr_buffer.getvalue()
    if stderr_content:
        print(json.dumps({
            "output_type": "stderr",
            "content": {"text": stderr_content},
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }))


if __name__ == "__main__":
    capture_output()