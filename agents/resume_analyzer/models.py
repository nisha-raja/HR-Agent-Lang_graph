"""
Data Models for Resume Analyzer Agent
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class ResumeData(BaseModel):
    """Model for resume input data"""
    content: str = Field(description="The full content of the resume")
    candidate_name: str = Field(description="Name of the candidate")
    candidate_email: str = Field(description="Email of the candidate", default="")
    file_name: str = Field(description="Name of the resume file")

class JobDescriptionData(BaseModel):
    """Model for job description data"""
    content: str = Field(description="The full content of the job description")
    job_title: str = Field(description="Title of the position")
    company_name: str = Field(description="Name of the hiring company")

class ResumeAnalysisRequest(BaseModel):
    """Request model for resume analysis"""
    resume_data: ResumeData
    job_description_data: JobDescriptionData

class ResumeAnalysisResponse(BaseModel):
    """Response model for resume analysis"""
    success: bool
    analysis_result: Optional[Dict[str, Any]] = None
    filename: Optional[str] = None
    message: str
    error: Optional[str] = None

class AnalysisResult(BaseModel):
    """Model for analysis results"""
    overall_score: int
    skills_analysis: Dict[str, Any]
    experience_analysis: Dict[str, Any]
    formatting_analysis: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    final_report: str
    analysis_date: str

class AnalysisHistory(BaseModel):
    """Model for analysis history"""
    candidate_name: str
    job_title: str
    company_name: str
    score: int
    analysis_date: str
    filename: str
