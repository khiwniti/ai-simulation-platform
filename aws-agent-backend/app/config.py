import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AWS AI Agent Engineering Platform"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:57890",
        "http://localhost:50191",
        "https://your-domain.com"
    ]
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    
    # Bedrock Configuration
    BEDROCK_AGENT_CORE_REGION: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # Nova Configuration
    NOVA_MODEL_ID: str = "amazon.nova-pro-v1:0"
    NOVA_API_ENDPOINT: str = ""
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/ai_agents"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: list = ["*"]  # Configure appropriately for production
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Agent Configuration
    MAX_AGENTS: int = 10
    MAX_CONCURRENT_TASKS: int = 5
    AGENT_TIMEOUT_SECONDS: int = 300
    
    # Physics Simulation
    PHYSICS_ENGINE: str = "cannon"
    MAX_SIMULATION_TIME: int = 3600  # 1 hour
    
    # File Storage
    S3_BUCKET_NAME: str = ""
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()