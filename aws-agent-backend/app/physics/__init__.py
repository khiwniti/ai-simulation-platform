"""
NVIDIA PhysX AI Integration for AWS AI Agent Platform
Provides GPU-accelerated physics simulation with AI-powered analysis
"""

from .nvidia_physics_engine import NVIDIAPhysicsEngine
from .physx_simulator import PhysXSimulator
from .omniverse_integration import OmniversePhysics
from .cuda_physics_solver import CUDAPhysicsSolver
from .ai_physics_analyzer import AIPhysicsAnalyzer

__version__ = "1.0.0"
__author__ = "AWS AI Agent Platform"

__all__ = [
    "NVIDIAPhysicsEngine",
    "PhysXSimulator", 
    "OmniversePhysics",
    "CUDAPhysicsSolver",
    "AIPhysicsAnalyzer"
]