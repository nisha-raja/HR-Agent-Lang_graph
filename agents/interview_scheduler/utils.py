"""
Utilities for Interview Scheduler Agent
"""

import json
import smtplib
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailManager:
    """Email management utilities for Interview Scheduler"""
    
    def __init__(self, config: Dict[str, Any]):
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_username = config.get('smtp_username')
        self.smtp_password = config.get('smtp_password')
        self.sender_email = config.get('sender_email')
        self.sender_name = config.get('sender_name', 'HR Team')
        self.email_enabled = bool(self.smtp_username and self.smtp_password and self.sender_email)
    
    def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email using SMTP"""
        if not self.email_enabled:
            return {
                'success': False,
                'error': 'email_not_configured',
                'message': f"Email sending is not configured. Would send to {to_email}: {subject}"
            }
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return {
                'success': True,
                'message': f"Email sent successfully to {to_email}",
                'message_id': str(uuid.uuid4())
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to send email: {str(e)}",
                'message': f"Error sending email to {to_email}"
            }
    
    def send_interview_invitation(self, candidate_email: str, interview_details: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """Send interview invitation email"""
        try:
            # Format email body with interview details
            body = template['body'].format(
                candidate_name=interview_details['candidate_name'],
                job_title=interview_details['job_title'],
                company_name=interview_details['company_name'],
                interview_date=interview_details['interview_date'],
                interview_time=interview_details['interview_time'],
                interview_type=interview_details['interview_type'],
                interviewer_name=interview_details['interviewer_name'],
                location=interview_details['location'],
                duration=interview_details['duration'],
                notes=interview_details.get('notes', '')
            )
            
            subject = template['subject'].format(
                job_title=interview_details['job_title'],
                company_name=interview_details['company_name']
            )
            
            return self.send_email(candidate_email, subject, body)
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to send interview invitation: {str(e)}",
                'message': f"Error sending interview invitation to {candidate_email}"
            }

class CalendarManager:
    """Calendar management utilities for Interview Scheduler"""
    
    def __init__(self, config: Dict[str, Any]):
        self.calendar_enabled = config['calendar_enabled']
        self.calendar_type = config['calendar_type']
        self.timezone = config['timezone']
    
    def create_calendar_event(self, interview_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create calendar event for interview"""
        if not self.calendar_enabled:
            return {
                'success': False,
                'error': 'Calendar integration is not enabled',
                'message': 'Calendar events cannot be created'
            }
        
        try:
            # Generate event details
            event_id = str(uuid.uuid4())
            title = f"Interview: {interview_details['candidate_name']} - {interview_details['job_title']}"
            
            description = f"""
            Interview Details:
            - Candidate: {interview_details['candidate_name']}
            - Position: {interview_details['job_title']}
            - Company: {interview_details['company_name']}
            - Type: {interview_details['interview_type']}
            - Duration: {interview_details['duration']}
            - Notes: {interview_details.get('notes', 'N/A')}
            """
            
            # For now, return mock calendar event
            # In a real implementation, you would integrate with Google Calendar, Outlook, etc.
            calendar_event = {
                'event_id': event_id,
                'title': title,
                'description': description,
                'start_time': f"{interview_details['interview_date']} {interview_details['interview_time']}",
                'end_time': self._calculate_end_time(interview_details['interview_date'], 
                                                   interview_details['interview_time'], 
                                                   interview_details['duration']),
                'attendees': [interview_details['candidate_email'], interview_details['interviewer_email']],
                'location': interview_details['location'],
                'status': 'confirmed'
            }
            
            return {
                'success': True,
                'calendar_event': calendar_event,
                'message': f"Calendar event created successfully: {event_id}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create calendar event: {str(e)}",
                'message': 'Error creating calendar event'
            }
    
    def _calculate_end_time(self, date: str, start_time: str, duration: str) -> str:
        """Calculate end time based on start time and duration"""
        try:
            # Parse duration (assuming format like "60 minutes" or "1 hour")
            duration_minutes = 60  # Default
            if 'minute' in duration.lower():
                duration_minutes = int(duration.split()[0])
            elif 'hour' in duration.lower():
                duration_minutes = int(duration.split()[0]) * 60
            
            # Calculate end time
            start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            
            return end_datetime.strftime("%Y-%m-%d %H:%M")
            
        except Exception:
            # Return default end time if parsing fails
            return f"{date} {start_time}"

class TemplateManager:
    """Email template management utilities"""
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default email templates"""
        default_templates = {
            "interview_invitation": {
                "template_id": "interview_invitation",
                "name": "Interview Invitation",
                "subject": "Interview Invitation - {job_title} at {company_name}",
                "body": """
                <html>
                <body>
                <h2>Interview Invitation</h2>
                <p>Dear {candidate_name},</p>
                <p>Thank you for your interest in the <strong>{job_title}</strong> position at <strong>{company_name}</strong>.</p>
                <p>We are pleased to invite you for an interview with the following details:</p>
                <ul>
                    <li><strong>Date:</strong> {interview_date}</li>
                    <li><strong>Time:</strong> {interview_time}</li>
                    <li><strong>Type:</strong> {interview_type}</li>
                    <li><strong>Duration:</strong> {duration}</li>
                    <li><strong>Interviewer:</strong> {interviewer_name}</li>
                    <li><strong>Location:</strong> {location}</li>
                </ul>
                {notes}
                <p>Please confirm your attendance by replying to this email.</p>
                <p>Best regards,<br>HR Team<br>{company_name}</p>
                </body>
                </html>
                """,
                "template_type": "interview_invitation",
                "is_active": True
            },
            "interview_confirmation": {
                "template_id": "interview_confirmation",
                "name": "Interview Confirmation",
                "subject": "Interview Confirmed - {job_title} at {company_name}",
                "body": """
                <html>
                <body>
                <h2>Interview Confirmed</h2>
                <p>Dear {candidate_name},</p>
                <p>Your interview for the <strong>{job_title}</strong> position at <strong>{company_name}</strong> has been confirmed.</p>
                <p><strong>Interview Details:</strong></p>
                <ul>
                    <li><strong>Date:</strong> {interview_date}</li>
                    <li><strong>Time:</strong> {interview_time}</li>
                    <li><strong>Type:</strong> {interview_type}</li>
                    <li><strong>Duration:</strong> {duration}</li>
                    <li><strong>Interviewer:</strong> {interviewer_name}</li>
                    <li><strong>Location:</strong> {location}</li>
                </ul>
                {notes}
                <p>We look forward to meeting you!</p>
                <p>Best regards,<br>HR Team<br>{company_name}</p>
                </body>
                </html>
                """,
                "template_type": "interview_confirmation",
                "is_active": True
            },
            "rejection": {
                "template_id": "rejection",
                "name": "Application Status Update",
                "subject": "Application Status - {job_title} at {company_name}",
                "body": """
                <html>
                <body>
                <h2>Application Status Update</h2>
                <p>Dear {candidate_name},</p>
                <p>Thank you for your interest in the <strong>{job_title}</strong> position at <strong>{company_name}</strong>.</p>
                <p>After careful consideration of your application, we regret to inform you that we have decided to move forward with other candidates whose qualifications more closely match our current needs.</p>
                <p>We appreciate the time you took to apply and wish you the best in your future endeavors.</p>
                <p>Best regards,<br>HR Team<br>{company_name}</p>
                </body>
                </html>
                """,
                "template_type": "rejection",
                "is_active": True
            }
        }
        
        # Save default templates
        for template_id, template in default_templates.items():
            template_path = self.templates_dir / f"{template_id}.json"
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    json.dump(template, f, indent=2, ensure_ascii=False)
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get email template by ID"""
        template_path = self.templates_dir / f"{template_id}.json"
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all available templates"""
        templates = []
        for template_file in self.templates_dir.glob("*.json"):
            with open(template_file, 'r', encoding='utf-8') as f:
                templates.append(json.load(f))
        return templates
    
    def save_template(self, template: Dict[str, Any]) -> bool:
        """Save email template"""
        try:
            template_id = template['template_id']
            template_path = self.templates_dir / f"{template_id}.json"
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving template: {e}")
            return False

class SchedulingManager:
    """Scheduling management utilities"""
    
    def __init__(self, config: Dict[str, Any]):
        self.score_thresholds = config['score_thresholds']
        self.auto_scheduling_rules = config['auto_scheduling_rules']
        self.available_time_slots = config['available_time_slots']
        self.default_duration = config['default_interview_duration']
    
    def get_scheduling_recommendation(self, score: int) -> Dict[str, Any]:
        """Get scheduling recommendation based on score"""
        if score >= self.score_thresholds['excellent']:
            return self.auto_scheduling_rules['excellent_score']
        elif score >= self.score_thresholds['good']:
            return self.auto_scheduling_rules['good_score']
        elif score >= self.score_thresholds['fair']:
            return self.auto_scheduling_rules['fair_score']
        else:
            return self.auto_scheduling_rules['poor_score']
    
    def suggest_interview_slots(self, date: str, duration: int = None) -> List[Dict[str, str]]:
        """Suggest available interview time slots for a given date"""
        if duration is None:
            duration = self.default_duration
        
        slots = []
        for time_slot in self.available_time_slots:
            slots.append({
                'date': date,
                'time': time_slot,
                'duration': f"{duration} minutes"
            })
        
        return slots
    
    def validate_interview_schedule(self, interview_details: Dict[str, Any]) -> Dict[str, Any]:
        """Validate interview schedule details"""
        errors = []
        
        # Check required fields
        required_fields = ['candidate_name', 'candidate_email', 'job_title', 'company_name', 
                          'interview_date', 'interview_time', 'interview_type', 'interviewer_name', 
                          'interviewer_email', 'location', 'duration']
        
        for field in required_fields:
            if not interview_details.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, interview_details.get('candidate_email', '')):
            errors.append("Invalid candidate email format")
        if not re.match(email_pattern, interview_details.get('interviewer_email', '')):
            errors.append("Invalid interviewer email format")
        
        # Validate date format
        try:
            datetime.strptime(interview_details.get('interview_date', ''), '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid interview date format (use YYYY-MM-DD)")
        
        # Validate time format
        try:
            datetime.strptime(interview_details.get('interview_time', ''), '%H:%M')
        except ValueError:
            errors.append("Invalid interview time format (use HH:MM)")
        
        if errors:
            return {
                'valid': False,
                'errors': errors,
                'message': 'Interview schedule validation failed'
            }
        else:
            return {
                'valid': True,
                'message': 'Interview schedule is valid'
            }
