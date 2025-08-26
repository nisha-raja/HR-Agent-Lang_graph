"""
FastAPI endpoints for Interview Scheduler Agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import uvicorn

from .agent import InterviewSchedulerAgent
from .models import (
    InterviewSchedulingRequest, InterviewSchedulingResponse,
    EmailRequest, EmailResponse, CandidateData
)

app = FastAPI(
    title="Interview Scheduler Agent API",
    description="API for scheduling interviews and managing candidates",
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
interview_scheduler = InterviewSchedulerAgent()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Interview Scheduler Agent API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        status = interview_scheduler.get_agent_status()
        return {
            "status": "healthy",
            "agent_status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/schedule", response_model=InterviewSchedulingResponse)
async def schedule_interview(request: InterviewSchedulingRequest):
    """Schedule an interview"""
    try:
        result = interview_scheduler.schedule_interview_from_dict(
            request.candidate_data.model_dump(),
            request.interview_details.model_dump()
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")

@app.post("/process-candidate")
async def process_candidate(candidate_data: CandidateData):
    """Process a candidate and get scheduling recommendations"""
    try:
        result = interview_scheduler.process_candidate(candidate_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/send-email", response_model=EmailResponse)
async def send_email(request: EmailRequest):
    """Send a custom email"""
    try:
        result = interview_scheduler.send_email(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")

@app.get("/templates")
async def get_email_templates():
    """Get all available email templates"""
    try:
        templates = interview_scheduler.get_email_templates()
        return {
            "success": True,
            "templates": templates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")

@app.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get specific email template"""
    try:
        template = interview_scheduler.get_template(template_id)
        if template:
            return {
                "success": True,
                "template": template
            }
        else:
            raise HTTPException(status_code=404, detail="Template not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")

@app.get("/slots")
async def suggest_interview_slots(date: str, duration: int = None):
    """Suggest available interview time slots"""
    try:
        slots = interview_scheduler.suggest_interview_slots(date, duration)
        return {
            "success": True,
            "slots": slots
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get slots: {str(e)}")

@app.get("/recommendation/{score}")
async def get_scheduling_recommendation(score: int):
    """Get scheduling recommendation based on score"""
    try:
        recommendation = interview_scheduler.get_scheduling_recommendation(score)
        return {
            "success": True,
            "recommendation": recommendation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation: {str(e)}")

@app.post("/validate-schedule")
async def validate_interview_schedule(interview_details: Dict[str, Any]):
    """Validate interview schedule details"""
    try:
        validation = interview_scheduler.validate_interview_schedule(interview_details)
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.get("/status")
async def get_agent_status():
    """Get agent status"""
    try:
        status = interview_scheduler.get_agent_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
