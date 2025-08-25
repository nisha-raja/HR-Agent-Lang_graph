"""
Data Models for Interview Scheduler Agent
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class CandidateData(BaseModel):
    """Model for candidate data"""
    name: str = Field(description="Candidate's full name")
    email: str = Field(description="Candidate's email address")
    score: int = Field(description="Resume analysis score")
    job_title: str = Field(description="Job title applied for")
    company_name: str = Field(description="Company name")
    resume_filename: str = Field(description="Resume file name", default="")
    analysis_date: str = Field(description="Date of analysis", default="")

class EmailTemplate(BaseModel):
    """Model for email templates"""
    template_id: str = Field(description="Unique template identifier")
    name: str = Field(description="Template name")
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body content")
    template_type: str = Field(description="Type of template (interview_invitation, rejection, etc.)")
    is_active: bool = Field(description="Whether template is active", default=True)

class InterviewDetails(BaseModel):
    """Model for interview details"""
    candidate_name: str = Field(description="Candidate's name")
    candidate_email: str = Field(description="Candidate's email")
    job_title: str = Field(description="Job title")
    company_name: str = Field(description="Company name")
    interview_date: str = Field(description="Interview date")
    interview_time: str = Field(description="Interview time")
    interview_type: str = Field(description="Interview type (phone, video, in-person)")
    interviewer_name: str = Field(description="Interviewer name")
    interviewer_email: str = Field(description="Interviewer email")
    location: str = Field(description="Interview location or meeting link")
    duration: str = Field(description="Interview duration")
    notes: str = Field(description="Additional notes", default="")

class InterviewSchedulingRequest(BaseModel):
    """Request model for interview scheduling"""
    candidate_data: CandidateData
    interview_details: InterviewDetails
    email_template_id: Optional[str] = None

class InterviewSchedulingResponse(BaseModel):
    """Response model for interview scheduling"""
    success: bool
    interview_id: Optional[str] = None
    email_sent: bool = False
    calendar_event_created: bool = False
    message: str
    error: Optional[str] = None

class EmailRequest(BaseModel):
    """Request model for email operations"""
    to_email: str
    subject: str
    body: str
    template_id: Optional[str] = None

class EmailResponse(BaseModel):
    """Response model for email operations"""
    success: bool
    message_id: Optional[str] = None
    message: str
    error: Optional[str] = None

class CalendarEvent(BaseModel):
    """Model for calendar events"""
    event_id: str = Field(description="Unique event identifier")
    title: str = Field(description="Event title")
    description: str = Field(description="Event description")
    start_time: str = Field(description="Event start time")
    end_time: str = Field(description="Event end time")
    attendees: List[str] = Field(description="List of attendee emails")
    location: str = Field(description="Event location or meeting link")
    status: str = Field(description="Event status", default="confirmed")

class SchedulingConfig(BaseModel):
    """Model for scheduling configuration"""
    default_interview_duration: int = Field(description="Default interview duration in minutes", default=60)
    available_time_slots: List[str] = Field(description="Available time slots", default=[])
    timezone: str = Field(description="Timezone for scheduling", default="UTC")
    auto_send_emails: bool = Field(description="Automatically send emails", default=True)
    auto_create_calendar_events: bool = Field(description="Automatically create calendar events", default=True)
