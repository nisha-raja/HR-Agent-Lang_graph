"""
FastAPI Gateway for Root Agent - Routes requests to appropriate sub-agents
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import uvicorn
import httpx
import asyncio

from .coordinator import RootAgentCoordinator

app = FastAPI(
    title="HR Agent Suite - Root Agent Gateway",
    description="API Gateway that routes requests to appropriate HR agents",
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

# Initialize the coordinator
coordinator = RootAgentCoordinator()

# Agent API endpoints
AGENT_ENDPOINTS = {
    "jd_generator": "http://localhost:8001",
    "resume_analyzer": "http://localhost:8002", 
    "interview_scheduler": "http://localhost:8003"
}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HR Agent Suite - Root Agent Gateway",
        "version": "1.0.0",
        "status": "healthy",
        "available_agents": coordinator.get_available_agents()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        status = coordinator.get_system_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/agents")
async def get_agents():
    """Get available agents"""
    try:
        agents = coordinator.get_available_agents()
        agent_statuses = {}
        
        for agent_name in agents:
            try:
                status = coordinator.get_agent_status(agent_name)
                agent_statuses[agent_name] = status
            except Exception as e:
                agent_statuses[agent_name] = {"status": "error", "error": str(e)}
        
        return {
            "success": True,
            "agents": agents,
            "statuses": agent_statuses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")

@app.get("/agents/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get status of a specific agent"""
    try:
        status = coordinator.get_agent_status(agent_name)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")

# ==================== JD GENERATOR ROUTING ====================

@app.post("/jd/generate")
async def generate_job_description(job_details: Dict[str, Any]):
    """Generate job description"""
    try:
        result = coordinator.generate_job_description(job_details)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD generation failed: {str(e)}")

@app.post("/jd/save")
async def save_job_description(request: Dict[str, Any]):
    """Save job description"""
    try:
        job_details = request.get("job_details", {})
        description = request.get("description", "")
        result = coordinator.save_job_description(job_details, description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD saving failed: {str(e)}")

@app.get("/jd/list")
async def get_job_descriptions():
    """Get available job descriptions"""
    try:
        result = coordinator.get_available_job_descriptions()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get JDs: {str(e)}")

@app.delete("/jd/{filename}")
async def delete_job_description(filename: str):
    """Delete job description"""
    try:
        result = coordinator.delete_job_description(filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD deletion failed: {str(e)}")

# ==================== RESUME ANALYZER ROUTING ====================

@app.post("/resume/analyze")
async def analyze_resume(request: Dict[str, Any]):
    """Analyze resume"""
    try:
        resume_data = request.get("resume_data", {})
        job_description_data = request.get("job_description_data", {})
        result = coordinator.analyze_resume(resume_data, job_description_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume analysis failed: {str(e)}")

@app.get("/resume/history")
async def get_analysis_history():
    """Get analysis history"""
    try:
        result = coordinator.get_analysis_history()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

# ==================== INTERVIEW SCHEDULER ROUTING ====================

@app.post("/interview/schedule")
async def schedule_interview(candidate_data: Dict[str, Any], interview_details: Dict[str, Any]):
    """Schedule interview"""
    try:
        result = coordinator.schedule_interview(candidate_data, interview_details)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview scheduling failed: {str(e)}")

@app.post("/interview/process-candidate")
async def process_candidate(candidate_data: Dict[str, Any]):
    """Process candidate"""
    try:
        result = coordinator.process_candidate(candidate_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Candidate processing failed: {str(e)}")

@app.get("/interview/templates")
async def get_email_templates():
    """Get email templates"""
    try:
        result = coordinator.get_email_templates()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")

@app.get("/interview/slots")
async def suggest_interview_slots(date: str, duration: int = None):
    """Suggest interview slots"""
    try:
        result = coordinator.suggest_interview_slots(date, duration)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get slots: {str(e)}")

# ==================== AI ASSISTANT ROUTING ====================

@app.post("/ai/assist")
async def ai_assistant(request: Dict[str, Any]):
    query = request.get("query", "")
    """AI assistant that routes queries to appropriate agents and parses job details"""
    try:
        query_lower = query.lower()
        
        # Check if this looks like a job description request
        job_keywords = ["developer", "engineer", "manager", "analyst", "specialist", "consultant", "designer", "architect", "salary", "experience", "company", "location", "skills", "remote", "full time", "part time"]
        
        if any(keyword in query_lower for keyword in job_keywords):
            # Parse job details from the query using LLM
            parsing_result = coordinator.parse_job_details_from_text(query)
            
            if parsing_result.get("success", False):
                # Successful parsing
                return {
                    "success": True,
                    "agent": "jd_generator",
                    "action": "parse_and_generate_job_description",
                    "message": parsing_result.get("message", "I've parsed your job requirements. Here are the extracted details:"),
                    "query": query,
                    "parsed_data": parsing_result.get("parsed_data", {}),
                    "suggested_action": "Navigate to Job Description Generator to review and generate the JD"
                }
            else:
                # Validation issues or errors
                return {
                    "success": False,
                    "agent": "jd_generator",
                    "action": "validation_required",
                    "message": parsing_result.get("message", "Please clarify the following issues:"),
                    "query": query,
                    "validation_issues": parsing_result.get("validation_issues", []),
                    "suggestions": parsing_result.get("suggestions", []),
                    "parsed_data": parsing_result.get("parsed_data", {}),
                    "suggested_action": "Please provide more details or correct the issues mentioned above"
                }
        
        elif any(word in query_lower for word in ["job", "jd", "generate", "create", "description"]):
            # Route to JD Generator
            return {
                "success": True,
                "agent": "jd_generator",
                "action": "generate_job_description",
                "message": "Routing to Job Description Generator",
                "query": query
            }
        
        elif any(word in query_lower for word in ["resume", "analyze", "candidate", "score", "evaluate"]):
            # Route to Resume Analyzer
            return {
                "success": True,
                "agent": "resume_analyzer", 
                "action": "analyze_resume",
                "message": "Routing to Resume Analyzer",
                "query": query
            }
        
        elif any(word in query_lower for word in ["interview", "schedule", "meeting", "calendar", "email"]):
            # Route to Interview Scheduler
            return {
                "success": True,
                "agent": "interview_scheduler",
                "action": "schedule_interview", 
                "message": "Routing to Interview Scheduler",
                "query": query
            }
        
        elif any(word in query_lower for word in ["status", "health", "check"]):
            # Get system status
            status = coordinator.get_system_status()
            return {
                "success": True,
                "agent": "root",
                "action": "system_status",
                "message": "System status retrieved",
                "status": status
            }
        
        else:
            # Default response
            return {
                "success": True,
                "agent": "root",
                "action": "general_query",
                "message": "I can help you with job descriptions, resume analysis, and interview scheduling. Please specify what you need.",
                "query": query
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI assistant failed: {str(e)}")

# ==================== BACKWARD COMPATIBILITY ====================

@app.post("/route/jd")
async def route_jd_request(job_details: Dict[str, Any]):
    """Backward compatibility for JD requests"""
    return await generate_job_description(job_details)

@app.post("/route/resume")
async def route_resume_request(resume_data: Dict[str, Any], job_description_data: Dict[str, Any]):
    """Backward compatibility for resume requests"""
    return await analyze_resume(resume_data, job_description_data)

@app.post("/route/interview")
async def route_interview_request(candidate_data: Dict[str, Any]):
    """Backward compatibility for interview requests"""
    return await process_candidate(candidate_data)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
