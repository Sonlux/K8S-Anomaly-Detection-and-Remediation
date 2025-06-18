from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import rag_utils for knowledge base querying
from k8s.backend.rag_utils import query_knowledge_base

app = FastAPI(title="Model Context Protocol (MCP) Server")

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
        # Here, you would integrate with your RAG system or other context providers
        # For now, we'll use the existing rag_utils to query the knowledge base
        
        # Example: Querying the knowledge base based on the user's query
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

        return MCPResponse(
            model_name=request.model_name,
            context=combined_context,
            source_documents=source_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP query failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "MCP Server is running"}

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
    # You can specify the port via an environment variable or directly
    port = int(os.getenv("MCP_SERVER_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)