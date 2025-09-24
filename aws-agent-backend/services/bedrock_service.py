import boto3
import json
import asyncio
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

from app.config import settings

logger = structlog.get_logger(__name__)

class BedrockService:
    """
    AWS Bedrock service integration for AI model interactions
    """
    
    def __init__(self):
        self.session = boto3.Session()
        self.bedrock_client = self.session.client(
            'bedrock-runtime',
            region_name=settings.AWS_REGION
        )
        self.bedrock_agent_client = self.session.client(
            'bedrock-agent-runtime',
            region_name=settings.AWS_REGION
        )
        
    async def health_check(self) -> Dict[str, Any]:
        """Check Bedrock service health"""
        try:
            # Test connection by listing available models
            response = self.bedrock_client.list_foundation_models()
            return {
                "status": "healthy",
                "models_available": len(response.get('modelSummaries', [])),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error("Bedrock health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def invoke_model(
        self, 
        model_id: str, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Invoke a Bedrock model with a prompt
        """
        try:
            # Prepare the request body based on model type
            if "anthropic.claude" in model_id:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            elif "amazon.titan" in model_id:
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": max_tokens,
                        "temperature": temperature,
                        "topP": 0.9
                    }
                }
            else:
                # Generic body structure
                body = {
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            
            # Invoke the model
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract text based on model type
            if "anthropic.claude" in model_id:
                text = response_body['content'][0]['text']
            elif "amazon.titan" in model_id:
                text = response_body['results'][0]['outputText']
            else:
                text = response_body.get('generated_text', '')
            
            return {
                "success": True,
                "text": text,
                "model_id": model_id,
                "usage": response_body.get('usage', {}),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Model invocation failed", model_id=model_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "model_id": model_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def invoke_agent(
        self,
        agent_id: str,
        session_id: str,
        input_text: str,
        enable_trace: bool = True
    ) -> Dict[str, Any]:
        """
        Invoke a Bedrock Agent
        """
        try:
            response = self.bedrock_agent_client.invoke_agent(
                agentId=agent_id,
                agentAliasId='TSTALIASID',  # Test alias
                sessionId=session_id,
                inputText=input_text,
                enableTrace=enable_trace
            )
            
            # Process streaming response
            result = {
                "success": True,
                "agent_id": agent_id,
                "session_id": session_id,
                "completion": "",
                "trace": [],
                "timestamp": datetime.now().isoformat()
            }
            
            for event in response.get('completion', []):
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        result["completion"] += chunk['bytes'].decode('utf-8')
                
                if 'trace' in event and enable_trace:
                    result["trace"].append(event['trace'])
            
            return result
            
        except Exception as e:
            logger.error("Agent invocation failed", agent_id=agent_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def create_knowledge_base_query(
        self,
        knowledge_base_id: str,
        query: str,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Query a Bedrock Knowledge Base
        """
        try:
            response = self.bedrock_agent_client.retrieve(
                knowledgeBaseId=knowledge_base_id,
                retrievalQuery={
                    'text': query
                },
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                }
            )
            
            results = []
            for result in response.get('retrievalResults', []):
                results.append({
                    "content": result.get('content', {}).get('text', ''),
                    "score": result.get('score', 0),
                    "metadata": result.get('metadata', {})
                })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "knowledge_base_id": knowledge_base_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Knowledge base query failed", kb_id=knowledge_base_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "knowledge_base_id": knowledge_base_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def list_agents(self) -> Dict[str, Any]:
        """
        List available Bedrock Agents
        """
        try:
            response = self.bedrock_agent_client.list_agents()
            
            agents = []
            for agent in response.get('agentSummaries', []):
                agents.append({
                    "agent_id": agent.get('agentId'),
                    "agent_name": agent.get('agentName'),
                    "description": agent.get('description'),
                    "status": agent.get('agentStatus'),
                    "updated_at": agent.get('updatedAt')
                })
            
            return {
                "success": True,
                "agents": agents,
                "count": len(agents),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to list agents", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_engineering_analysis(
        self,
        problem_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate engineering analysis using Bedrock
        """
        prompt = f"""You are an expert engineering AI assistant specializing in mechanical, structural, and systems engineering. 

Problem Description:
{problem_description}

Context: {json.dumps(context, indent=2) if context else 'No additional context provided'}

Please provide a comprehensive engineering analysis including:
1. Problem understanding and requirements
2. Engineering principles applicable
3. Potential solution approaches
4. Key calculations or formulations needed
5. Design considerations and constraints
6. Recommended next steps

Format your response as a structured engineering analysis."""

        return await self.invoke_model(
            model_id=settings.BEDROCK_MODEL_ID,
            prompt=prompt,
            max_tokens=2000,
            temperature=0.3
        )