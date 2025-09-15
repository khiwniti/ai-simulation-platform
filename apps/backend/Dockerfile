FROM nvidia/cuda:12.0-devel-ubuntu22.04

# Install Python, Docker, and system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-pip \
    python3.11-dev \
    build-essential \
    docker.io \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
RUN update-alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 1

WORKDIR /app

# Copy requirements and install Python dependencies
COPY apps/backend/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY apps/backend/ .

# Expose port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]