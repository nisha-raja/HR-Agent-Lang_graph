"""
Interview Scheduler Agent Package
"""

from .interview_scheduler_agent import InterviewSchedulerAgent as OldInterviewSchedulerAgent, CandidateData, EmailTemplate, InterviewDetails
from .agent import InterviewSchedulerAgent
from .models import (
    InterviewSchedulingRequest, InterviewSchedulingResponse, 
    EmailRequest, EmailResponse, CalendarEvent, SchedulingConfig
)
from .config import InterviewSchedulerConfig
from .utils import EmailManager, CalendarManager, TemplateManager, SchedulingManager

# Export main classes
__all__ = [
    'InterviewSchedulerAgent',
    'CandidateData', 
    'EmailTemplate', 
    'InterviewDetails',
    'InterviewSchedulingRequest',
    'InterviewSchedulingResponse',
    'EmailRequest',
    'EmailResponse',
    'CalendarEvent',
    'SchedulingConfig',
    'InterviewSchedulerConfig',
    'EmailManager',
    'CalendarManager',
    'TemplateManager',
    'SchedulingManager'
]

# For backward compatibility
OldInterviewSchedulerAgent = OldInterviewSchedulerAgent
