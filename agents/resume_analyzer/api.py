"""
FastAPI endpoints for Resume Analyzer Agent
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import uvicorn

from .agent import ResumeAnalyzerAgent
from .models import ResumeAnalysisRequest, ResumeAnalysisResponse

app = FastAPI(
    title="Resume Analyzer Agent API",
    description="API for analyzing resumes against job descriptions",
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

# Initialize the agent
resume_analyzer = ResumeAnalyzerAgent()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Resume Analyzer Agent API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        status = resume_analyzer.get_agent_status()
        return {
            "status": "healthy",
            "agent_status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(request: ResumeAnalysisRequest):
    """Analyze a resume against a job description"""
    try:
        result = resume_analyzer.analyze_resume_from_dict(
            request.resume_data.model_dump(),
            request.job_description_data.model_dump()
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-upload")
async def analyze_resume_upload(
    resume_file: UploadFile = File(...),
    job_description_data: Dict[str, Any] = None
):
    """Analyze a resume from uploaded file"""
    try:
        # Read uploaded file
        content = await resume_file.read()
        file_content = content.decode('utf-8')
        
        # Create resume data
        resume_data = {
            "content": file_content,
            "candidate_name": resume_file.filename.split('.')[0],
            "candidate_email": "",
            "file_name": resume_file.filename
        }
        
        # Analyze resume
        result = resume_analyzer.analyze_resume_from_dict(
            resume_data,
            job_description_data or {}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/history")
async def get_analysis_history():
    """Get analysis history"""
    try:
        history = resume_analyzer.get_analysis_history()
        return {
            "success": True,
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.get("/status")
async def get_agent_status():
    """Get agent status"""
    try:
        status = resume_analyzer.get_agent_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
