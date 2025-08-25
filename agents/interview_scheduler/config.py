"""
Configuration Management for Interview Scheduler Agent
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InterviewSchedulerConfig:
    """Configuration for Interview Scheduler Agent"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.scheduling_dir = self.data_dir / "scheduling"
        self.email_templates_dir = self.data_dir / "email_templates"
        
        # Ensure directories exist
        self.scheduling_dir.mkdir(parents=True, exist_ok=True)
        self.email_templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Email Configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_name = os.getenv("SENDER_NAME", "HR Team")
        
        # Calendar Configuration
        self.calendar_enabled = os.getenv("CALENDAR_ENABLED", "false").lower() == "true"
        self.calendar_type = os.getenv("CALENDAR_TYPE", "google")  # google, outlook, etc.
        self.calendar_credentials_file = os.getenv("CALENDAR_CREDENTIALS_FILE")
        
        # Scheduling Configuration
        self.default_interview_duration = int(os.getenv("DEFAULT_INTERVIEW_DURATION", "60"))
        self.timezone = os.getenv("TIMEZONE", "UTC")
        self.auto_send_emails = os.getenv("AUTO_SEND_EMAILS", "true").lower() == "true"
        self.auto_create_calendar_events = os.getenv("AUTO_CREATE_CALENDAR_EVENTS", "true").lower() == "true"
        
        # Available time slots (9 AM to 5 PM by default)
        self.available_time_slots = [
            "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
            "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
            "15:00", "15:30", "16:00", "16:30", "17:00"
        ]
        
        # Interview types
        self.interview_types = [
            "phone",
            "video",
            "in-person",
            "technical",
            "behavioral",
            "panel"
        ]
        
        # Email templates configuration
        self.default_templates = {
            "interview_invitation": {
                "name": "Interview Invitation",
                "subject": "Interview Invitation - {job_title} at {company_name}",
                "template_type": "interview_invitation"
            },
            "interview_confirmation": {
                "name": "Interview Confirmation",
                "subject": "Interview Confirmed - {job_title} at {company_name}",
                "template_type": "interview_confirmation"
            },
            "interview_reschedule": {
                "name": "Interview Reschedule",
                "subject": "Interview Reschedule Request - {job_title} at {company_name}",
                "template_type": "interview_reschedule"
            },
            "rejection": {
                "name": "Application Status Update",
                "subject": "Application Status - {job_title} at {company_name}",
                "template_type": "rejection"
            }
        }
        
        # Scoring thresholds for automatic scheduling
        self.score_thresholds = {
            "excellent": 85,
            "good": 70,
            "fair": 50,
            "poor": 0
        }
        
        # Auto-scheduling rules
        self.auto_scheduling_rules = {
            "excellent_score": {
                "auto_schedule": True,
                "priority": "high",
                "response_time": "24h"
            },
            "good_score": {
                "auto_schedule": True,
                "priority": "medium",
                "response_time": "48h"
            },
            "fair_score": {
                "auto_schedule": False,
                "priority": "low",
                "response_time": "72h"
            },
            "poor_score": {
                "auto_schedule": False,
                "priority": "none",
                "response_time": "1 week"
            }
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'smtp_username': self.smtp_username,
            'sender_email': self.sender_email,
            'sender_name': self.sender_name,
            'calendar_enabled': self.calendar_enabled,
            'calendar_type': self.calendar_type,
            'default_interview_duration': self.default_interview_duration,
            'timezone': self.timezone,
            'auto_send_emails': self.auto_send_emails,
            'auto_create_calendar_events': self.auto_create_calendar_events,
            'available_time_slots': self.available_time_slots,
            'interview_types': self.interview_types,
            'score_thresholds': self.score_thresholds,
            'auto_scheduling_rules': self.auto_scheduling_rules
        }
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        # Check email configuration (only if auto_send_emails is enabled)
        if self.auto_send_emails:
            if not self.smtp_username or not self.smtp_password:
                print("⚠️ Warning: SMTP credentials not configured. Auto-sending emails will be disabled.")
                self.auto_send_emails = False
            if not self.sender_email:
                print("⚠️ Warning: SENDER_EMAIL not configured. Auto-sending emails will be disabled.")
                self.auto_send_emails = False
        
        # Check calendar configuration (only if calendar is enabled)
        if self.calendar_enabled and self.calendar_type == "google":
            if not self.calendar_credentials_file:
                print("⚠️ Warning: CALENDAR_CREDENTIALS_FILE not configured. Calendar integration will be disabled.")
                self.calendar_enabled = False
        
        # Check directories
        if not self.scheduling_dir.exists():
            raise ValueError(f"Scheduling directory does not exist: {self.scheduling_dir}")
        
        if not self.email_templates_dir.exists():
            raise ValueError(f"Email templates directory does not exist: {self.email_templates_dir}")
        
        return True
