from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Ensure backend directory is in sys.path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agentic_rag_cli import KubernetesAgenticRAG

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = KubernetesAgenticRAG(debug=True)

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_input = data.get("message", "")
    response = rag.chat(user_input)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
