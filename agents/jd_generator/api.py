"""
REST API for JD Generator Agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn

from .agent import JDGeneratorAgent
from .models import JobDetails, JobDescriptionResponse, RAGStats

# Initialize FastAPI app
app = FastAPI(
    title="JD Generator Agent API",
    description="REST API for AI-powered job description generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = JDGeneratorAgent()

# Request/Response models for API
class GenerateJDRequest(BaseModel):
    job_details: Dict[str, Any]

class SaveJDRequest(BaseModel):
    job_details: Dict[str, Any]
    job_description: str

class DeleteJDRequest(BaseModel):
    filename: str

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "JD Generator Agent API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        status = agent.get_agent_status()
        return {
            "status": "healthy",
            "agent_status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent health check failed: {str(e)}")

@app.post("/generate", response_model=JobDescriptionResponse)
async def generate_job_description(request: GenerateJDRequest):
    """Generate a job description"""
    try:
        response = agent.generate_job_description_from_dict(request.job_details)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/save", response_model=JobDescriptionResponse)
async def save_job_description(request: SaveJDRequest):
    """Save a job description"""
    try:
        response = agent.save_job_description(request.job_details, request.job_description)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")

@app.get("/job-descriptions")
async def get_job_descriptions():
    """Get all available job descriptions"""
    try:
        job_descriptions = agent.get_available_job_descriptions()
        return {
            "success": True,
            "job_descriptions": job_descriptions,
            "count": len(job_descriptions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job descriptions: {str(e)}")

@app.delete("/job-descriptions/{filename}")
async def delete_job_description(filename: str):
    """Delete a job description"""
    try:
        response = agent.delete_job_description(filename)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@app.get("/rag-stats")
async def get_rag_stats():
    """Get RAG system statistics"""
    try:
        stats = agent.get_rag_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get RAG stats: {str(e)}")

@app.get("/config")
async def get_config():
    """Get agent configuration"""
    try:
        config = agent.config.get_config()
        return {
            "success": True,
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get config: {str(e)}")

@app.get("/status")
async def get_status():
    """Get comprehensive agent status"""
    try:
        status = agent.get_agent_status()
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

# Run the API server
if __name__ == "__main__":
    uvicorn.run(
        "agents.jd_generator.api:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
