# Physics-enabled Python execution environment with NVIDIA PhysX AI support
FROM nvidia/cuda:12.2-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=""

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    gcc \
    g++ \
    cmake \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python
RUN ln -s /usr/bin/python3.11 /usr/bin/python

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install Python packages for scientific computing and physics
RUN pip install --no-cache-dir \
    numpy==1.24.3 \
    matplotlib==3.7.1 \
    pandas==2.0.3 \
    scipy==1.11.1 \
    sympy==1.12 \
    plotly==5.15.0 \
    seaborn==0.12.2 \
    pillow==10.0.0 \
    ipython==8.14.0 \
    pynvml==11.5.0 \
    cupy-cuda12x==12.2.0 \
    numba==0.58.1

# Install physics simulation libraries
RUN pip install --no-cache-dir \
    pybullet==3.2.5 \
    pymunk==6.5.1 \
    moderngl==5.8.2 \
    moderngl-window==2.4.4

# Create physics libraries directory
RUN mkdir -p /opt/physics

# Note: In a real implementation, you would install NVIDIA PhysX AI here
# For now, we'll create a placeholder structure
RUN mkdir -p /opt/physx-ai/lib /opt/physx-ai/include
RUN echo "# PhysX AI placeholder" > /opt/physx-ai/lib/libphysx_ai.so

# Set up PhysX environment
ENV PHYSX_AI_ROOT=/opt/physx-ai
ENV LD_LIBRARY_PATH=/opt/physx-ai/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH=/opt/physx-ai/python:$PYTHONPATH

# Create non-root user for security
RUN useradd -m -u 1000 executor
USER executor
WORKDIR /home/executor

# Set up execution environment
ENV PYTHONPATH=/home/executor:/opt/physx-ai/python
ENV MPLBACKEND=Agg

# Copy physics execution script
COPY physics_execute.py /home/executor/execute.py

CMD ["python", "-u", "/home/executor/execute.py"]