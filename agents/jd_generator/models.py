"""
Data Models for JD Generator Agent
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class JobDetails(BaseModel):
    """Model for job details input"""
    job_title: str = Field(description="The title of the position")
    experience_required: str = Field(description="Required experience level")
    company_name: str = Field(description="Name of the hiring company")
    employment_type: str = Field(description="Full-time, Part-time, Contract, etc.")
    salary_range: str = Field(description="Salary range according to market standards")
    industry: str = Field(description="Industry or sector", default="Technology")
    location: str = Field(description="Job location", default="Remote")
    department: str = Field(description="Department or team", default="General")

class JobDescriptionRequest(BaseModel):
    """Request model for job description generation"""
    job_details: JobDetails

class JobDescriptionResponse(BaseModel):
    """Response model for job description generation"""
    success: bool
    job_description: Optional[str] = None
    job_details: Optional[Dict[str, Any]] = None
    filename: Optional[str] = None
    metadata_filename: Optional[str] = None
    message: str
    error: Optional[str] = None

class ValidationResult(BaseModel):
    """Validation result model"""
    valid: bool
    message: str
    missing_fields: List[str] = []

class RAGStats(BaseModel):
    """RAG system statistics"""
    status: str
    documents: int
    method: str
    error: Optional[str] = None
