from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import sys
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configuration management
from backend.src.config.loader import (
    get_config, setup_logging, validate_environment, ensure_data_directories
)

# Import rag_utils for knowledge base querying
from backend.src.utils.rag_utils import query_knowledge_base

# Setup logging and configuration
setup_logging()
logger = logging.getLogger(__name__)

# Validate environment
if not validate_environment():
    logger.error("Environment validation failed. Please check your configuration.")
    sys.exit(1)

# Ensure data directories exist
ensure_data_directories()

# Get configuration
app_config = get_config()

app = FastAPI(
    title="Model Context Protocol (MCP) Server",
    description="MCP server for Kubernetes monitoring system",
    version="1.0.0"
)

class MCPRequest(BaseModel):
    model_name: str
    query: str
    context_type: str = "general"

class MCPResponse(BaseModel):
    model_name: str
    context: str
    source_documents: list = []

@app.post("/mcp/query", response_model=MCPResponse)
async def mcp_query(request: MCPRequest):
    """Endpoint for Model Context Protocol (MCP) queries."""
    try:
        logger.info(f"Received MCP query for model '{request.model_name}': {request.query}")
        
        # Query the knowledge base using the RAG system
        results = query_knowledge_base(request.query)
        
        context_docs = [doc.page_content for doc in results]
        source_info = [{
            "page_content": doc.page_content,
            "metadata": doc.metadata
        } for doc in results]

        # Combine the retrieved documents into a single context string
        combined_context = "\n\n".join(context_docs)

        if not combined_context:
            combined_context = "No relevant context found for your query."
            logger.warning(f"No context found for query: {request.query}")
        else:
            logger.info(f"Found {len(results)} relevant documents for query")

        return MCPResponse(
            model_name=request.model_name,
            context=combined_context,
            source_documents=source_info
        )
    except Exception as e:
        logger.error(f"MCP query failed: {e}")
        raise HTTPException(status_code=500, detail=f"MCP query failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not app_config.monitoring.enable_health_checks:
        raise HTTPException(status_code=404, detail="Health checks disabled")
    
    return {
        "status": "ok", 
        "message": "MCP Server is running",
        "configuration": {
            "port": app_config.api.mcp_server_port,
            "log_level": app_config.logging.level
        }
    }

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Model Context Protocol Server!"}

@app.post("/mcp/predict")
async def predict(request: dict):
    """
    Placeholder for Model Context Protocol (MCP) prediction endpoint.
    Accepts a dictionary as input and returns a simple response.
    """
    # In a real implementation, you would process the request data
    # with your model and return the prediction.
    print(f"Received MCP predict request: {request}")
    response_data = {"status": "success", "message": "Prediction received", "input_data": request}
    return response_data

@app.post("/mcp/train")
async def train(request: dict):
    """
    Placeholder for Model Context Protocol (MCP) training endpoint.
    Accepts training parameters and initiates a training process.
    """
    print(f"Received MCP train request: {request}")
    return {"status": "success", "message": "Training request received", "training_params": request}

@app.post("/mcp/evaluate")
async def evaluate(request: dict):
    """
    Placeholder for Model Context Protocol (MCP) evaluation endpoint.
    Accepts evaluation parameters and returns evaluation metrics.
    """
    print(f"Received MCP evaluate request: {request}")
    return {"status": "success", "message": "Evaluation request received", "evaluation_params": request}

@app.get("/mcp/status")
async def status():
    """
    Placeholder for Model Context Protocol (MCP) status endpoint.
    Returns the current status of the model or server.
    """
    print("Received MCP status request")
    return {"status": "success", "message": "MCP server is operational"}

@app.get("/mcp/health")
async def health():
    """
    Placeholder for Model Context Protocol (MCP) health check endpoint.
    Returns a simple health status.
    """
    print("Received MCP health request")
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info(f"Starting MCP server on {app_config.api.api_server_host}:{app_config.api.mcp_server_port}")
    uvicorn.run(
        app, 
        host=app_config.api.api_server_host, 
        port=app_config.api.mcp_server_port,
        log_level=app_config.logging.level.lower()
    )