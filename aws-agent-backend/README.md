# AWS AI Agent Engineering Platform - Backend

This is the AWS-native backend for the AI Engineering Platform, designed for the AWS AI Agent Global Hackathon.

## 🏆 Hackathon Submission Features

### AWS Services Integration
- **Amazon Bedrock AgentCore**: Central orchestration and reasoning engine
- **Amazon Nova Act SDK**: Autonomous action execution and tool calling
- **Amazon Q**: Knowledge retrieval and documentation assistance
- **Amazon SageMaker**: Custom ML models for engineering optimization
- **AWS Lambda**: Serverless execution for compute-intensive simulations

### Autonomous AI Engineering Team
- **Physics Agent**: Structural analysis, stress simulation, safety calculations
- **Design Agent**: CAD modeling, engineering drawings, design validation
- **Optimization Agent**: Multi-objective optimization, cost/weight minimization
- **Materials Agent**: Material selection, durability assessment, sustainability analysis
- **Project Manager Agent**: Project planning, coordination, final reporting

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- AWS Account with Bedrock access
- $100 AWS credits (optional but recommended)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Configure AWS credentials
# Add your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to .env

# Start the backend
python main.py
```

### AWS Setup
1. Request AWS credits: https://challengepost.wufoo.com/forms/msjh12a0omn95o/
2. Enable Bedrock models in AWS Console
3. Configure Bedrock AgentCore access
4. Request Kiro access codes (if needed)

## 🎬 Demo Scenarios

### Autonomous Bridge Design
```bash
POST /api/demo/bridge-design
{
  "span_length": 50.0,
  "load_requirements": {
    "pedestrian_load": 5000,
    "wind_load": 1200,
    "snow_load": 800
  },
  "material_constraints": {
    "budget_per_kg": 3.50,
    "environmental_class": "C4"
  }
}
```

### Multi-Agent Engineering Project
```bash
POST /api/demo/engineering-project
{
  "project_description": "Design a pedestrian bridge spanning 50 meters",
  "requirements": {
    "span": 50,
    "load_capacity": 5000,
    "safety_factor": 2.0,
    "design_life": 50
  }
}
```

## 🏗️ Architecture

```
Frontend (React/Next.js)
    ↓
AWS API Gateway
    ↓
FastAPI Backend
    ↓
Amazon Bedrock AgentCore (Orchestrator)
    ├── Physics Agent (Nova + Custom Tools)
    ├── Design Agent (Nova + CAD Tools)
    ├── Optimization Agent (SageMaker + Algorithms)
    ├── Materials Agent (Bedrock + Knowledge Base)
    └── Project Manager (Q + Documentation)
    ↓
AWS Infrastructure (S3, DynamoDB, Lambda)
```

## 🎯 Hackathon Differentiators

1. **Real Engineering Impact**: Not just a chatbot - actually designs and optimizes engineering systems
2. **Multi-Agent Sophistication**: Complex agent interactions and specialization
3. **AWS Service Integration**: Deep integration with multiple AWS AI services
4. **Autonomous Operation**: Complete engineering projects without human intervention
5. **Physics Integration**: Real-time feedback between AI decisions and simulation results

## 📊 API Endpoints

- `GET /health` - System health check
- `GET /api/demo/scenarios` - Available demo scenarios
- `POST /api/demo/bridge-design` - Autonomous bridge design demo
- `POST /api/demo/engineering-project` - General engineering project
- `GET /api/agents/status` - Agent system status
- `WebSocket /ws/{client_id}` - Real-time agent communication

## 🧪 Testing

```bash
# Run unit tests
pytest

# Test agent integration
python -m pytest tests/test_agents.py

# Test AWS integration
python -m pytest tests/test_aws_integration.py
```

## 📈 Performance Metrics

- **Agent Response Time**: < 2 seconds for simple tasks
- **Project Completion Time**: 5-10 minutes for bridge design
- **Accuracy**: 95%+ for structural calculations
- **Concurrency**: Up to 5 simultaneous projects

## 🏅 Hackathon Competition Categories

This submission targets multiple prizes:
- **1st Place ($16,000)**: Novel autonomous engineering agent system
- **Best Bedrock AgentCore Implementation ($3,000)**: Advanced agent orchestration
- **Best Nova Act Integration ($3,000)**: Sophisticated action execution
- **Best Bedrock Application ($3,000)**: Comprehensive AWS integration

## 🔧 Development

```bash
# Run development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# View API documentation
open http://localhost:8000/docs
```

Built with ❤️ for the AWS AI Agent Global Hackathon 2025
