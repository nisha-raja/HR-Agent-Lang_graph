"""
Pure Interview Scheduler Agent - Self-contained interview scheduling
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, TypedDict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .models import (
    CandidateData, InterviewDetails, InterviewSchedulingRequest, 
    InterviewSchedulingResponse, EmailRequest, EmailResponse, 
    CalendarEvent, SchedulingConfig
)
from .config import InterviewSchedulerConfig
from .utils import EmailManager, CalendarManager, TemplateManager, SchedulingManager

class InterviewSchedulingState(TypedDict):
    """State for the interview scheduling workflow"""
    candidate_data: CandidateData
    interview_details: InterviewDetails
    scheduling_recommendation: Dict[str, Any]
    email_template: Dict[str, Any]
    email_sent: bool
    calendar_event_created: bool
    interview_id: str
    current_step: str
    messages: List[Dict[str, Any]]

class InterviewSchedulerAgent:
    """Pure Interview Scheduler Agent - Self-contained and deployable independently"""
    
    def __init__(self):
        # Initialize configuration
        self.config = InterviewSchedulerConfig()
        self.config.validate_config()
        
        # Initialize utilities
        self.email_manager = EmailManager(self.config.get_config())
        self.calendar_manager = CalendarManager(self.config.get_config())
        self.template_manager = TemplateManager(self.config.email_templates_dir)
        self.scheduling_manager = SchedulingManager(self.config.get_config())
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.3")),
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def analyze_candidate_score(self, state: InterviewSchedulingState) -> InterviewSchedulingState:
        """Analyze candidate score and get scheduling recommendation"""
        candidate_data = state['candidate_data']
        
        # Get scheduling recommendation based on score
        recommendation = self.scheduling_manager.get_scheduling_recommendation(candidate_data.score)
        
        # Generate AI-powered scheduling insights
        prompt = f"""
        Analyze the candidate's profile and provide scheduling recommendations.
        
        Candidate: {candidate_data.name}
        Job Title: {candidate_data.job_title}
        Company: {candidate_data.company_name}
        Score: {candidate_data.score}/100
        
        Scheduling Recommendation: {recommendation}
        
        Provide insights on:
        1. Priority level for scheduling
        2. Recommended interview type
        3. Suggested interview duration
        4. Any special considerations
        5. Follow-up timeline
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        state['scheduling_recommendation'] = {
            'recommendation': recommendation,
            'ai_insights': response.content,
            'priority': recommendation.get('priority', 'medium'),
            'auto_schedule': recommendation.get('auto_schedule', False),
            'response_time': recommendation.get('response_time', '48h')
        }
        state['current_step'] = "score_analyzed"
        
        state['messages'].append({
            "role": "user",
            "content": f"Analyzed scheduling recommendation for {candidate_data.name}"
        })
        
        return state
    
    def select_email_template(self, state: InterviewSchedulingState) -> InterviewSchedulingState:
        """Select appropriate email template based on candidate score"""
        candidate_data = state['candidate_data']
        recommendation = state['scheduling_recommendation']
        
        # Select template based on score and recommendation
        if candidate_data.score >= 70:  # Good or excellent score
            template_id = "interview_invitation"
        else:
            template_id = "rejection"
        
        # Get the template
        template = self.template_manager.get_template(template_id)
        
        if not template:
            # Fallback to default template
            template = self.template_manager.get_template("interview_invitation")
        
        state['email_template'] = template
        state['current_step'] = "template_selected"
        
        state['messages'].append({
            "role": "user",
            "content": f"Selected email template: {template.get('name', 'Unknown')}"
        })
        
        return state
    
    def send_interview_email(self, state: InterviewSchedulingState) -> InterviewSchedulingState:
        """Send interview invitation email"""
        candidate_data = state['candidate_data']
        interview_details = state['interview_details']
        template = state['email_template']
        
        # Send email
        email_result = self.email_manager.send_interview_invitation(
            candidate_data.email,
            interview_details.model_dump(),
            template
        )
        
        state['email_sent'] = email_result['success']
        state['current_step'] = "email_sent"
        
        state['messages'].append({
            "role": "user",
            "content": f"Email sent: {email_result['success']} - {email_result.get('message', '')}"
        })
        
        return state
    
    def create_calendar_event(self, state: InterviewSchedulingState) -> InterviewSchedulingState:
        """Create calendar event for interview"""
        interview_details = state['interview_details']
        
        # Create calendar event
        calendar_result = self.calendar_manager.create_calendar_event(
            interview_details.model_dump()
        )
        
        state['calendar_event_created'] = calendar_result['success']
        state['current_step'] = "calendar_created"
        
        state['messages'].append({
            "role": "user",
            "content": f"Calendar event created: {calendar_result['success']} - {calendar_result.get('message', '')}"
        })
        
        return state
    
    def finalize_scheduling(self, state: InterviewSchedulingState) -> InterviewSchedulingState:
        """Finalize the scheduling process"""
        # Generate interview ID
        interview_id = str(uuid.uuid4())
        state['interview_id'] = interview_id
        state['current_step'] = "complete"
        
        state['messages'].append({
            "role": "user",
            "content": f"Interview scheduling completed with ID: {interview_id}"
        })
        
        return state
    
    def schedule_interview(self, candidate_data: CandidateData, interview_details: InterviewDetails) -> Dict[str, Any]:
        """Schedule an interview for a candidate"""
        try:
            # Initialize state
            state = InterviewSchedulingState(
                candidate_data=candidate_data,
                interview_details=interview_details,
                scheduling_recommendation={},
                email_template={},
                email_sent=False,
                calendar_event_created=False,
                interview_id="",
                current_step="start",
                messages=[]
            )
            
            # Execute workflow steps
            state = self.analyze_candidate_score(state)
            state = self.select_email_template(state)
            state = self.send_interview_email(state)
            state = self.create_calendar_event(state)
            state = self.finalize_scheduling(state)
            
            return {
                'success': True,
                'interview_id': state['interview_id'],
                'email_sent': state['email_sent'],
                'calendar_event_created': state['calendar_event_created'],
                'scheduling_recommendation': state['scheduling_recommendation'],
                'messages': state['messages']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'scheduling_failed',
                'message': f'Error scheduling interview: {str(e)}'
            }
    
    def schedule_interview_from_dict(self, candidate_data: Dict[str, Any], interview_details: Dict[str, Any]) -> InterviewSchedulingResponse:
        """Schedule interview from dictionary input"""
        try:
            # Validate input
            validation = self.scheduling_manager.validate_interview_schedule(interview_details)
            if not validation['valid']:
                return InterviewSchedulingResponse(
                    success=False,
                    error='validation_failed',
                    message=validation['message']
                )
            
            # Create CandidateData object
            candidate_obj = CandidateData(
                name=candidate_data['name'],
                email=candidate_data['email'],
                score=candidate_data['score'],
                job_title=candidate_data['job_title'],
                company_name=candidate_data['company_name'],
                resume_filename=candidate_data.get('resume_filename', ''),
                analysis_date=candidate_data.get('analysis_date', '')
            )
            
            # Create InterviewDetails object
            interview_obj = InterviewDetails(
                candidate_name=interview_details['candidate_name'],
                candidate_email=interview_details['candidate_email'],
                job_title=interview_details['job_title'],
                company_name=interview_details['company_name'],
                interview_date=interview_details['interview_date'],
                interview_time=interview_details['interview_time'],
                interview_type=interview_details['interview_type'],
                interviewer_name=interview_details['interviewer_name'],
                interviewer_email=interview_details['interviewer_email'],
                location=interview_details['location'],
                duration=interview_details['duration'],
                notes=interview_details.get('notes', '')
            )
            
            # Schedule interview
            result = self.schedule_interview(candidate_obj, interview_obj)
            
            if not result['success']:
                return InterviewSchedulingResponse(
                    success=False,
                    error=result.get('error'),
                    message=result.get('message', 'Scheduling failed')
                )
            
            return InterviewSchedulingResponse(
                success=True,
                interview_id=result['interview_id'],
                email_sent=result['email_sent'],
                calendar_event_created=result['calendar_event_created'],
                message='Interview scheduled successfully'
            )
            
        except Exception as e:
            return InterviewSchedulingResponse(
                success=False,
                error='scheduling_failed',
                message=f'Error scheduling interview: {str(e)}'
            )
    
    def send_email(self, email_request: EmailRequest) -> EmailResponse:
        """Send a custom email"""
        try:
            result = self.email_manager.send_email(
                email_request.to_email,
                email_request.subject,
                email_request.body
            )
            
            if result['success']:
                return EmailResponse(
                    success=True,
                    message_id=result.get('message_id'),
                    message=result['message']
                )
            else:
                return EmailResponse(
                    success=False,
                    error=result.get('error'),
                    message=result['message']
                )
                
        except Exception as e:
            return EmailResponse(
                success=False,
                error='email_failed',
                message=f'Error sending email: {str(e)}'
            )
    
    def get_email_templates(self) -> List[Dict[str, Any]]:
        """Get all available email templates"""
        return self.template_manager.get_all_templates()
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get specific email template"""
        return self.template_manager.get_template(template_id)
    
    def save_template(self, template: Dict[str, Any]) -> bool:
        """Save email template"""
        return self.template_manager.save_template(template)
    
    def suggest_interview_slots(self, date: str, duration: int = None) -> List[Dict[str, str]]:
        """Suggest available interview time slots"""
        return self.scheduling_manager.suggest_interview_slots(date, duration)
    
    def get_scheduling_recommendation(self, score: int) -> Dict[str, Any]:
        """Get scheduling recommendation based on score"""
        return self.scheduling_manager.get_scheduling_recommendation(score)
    
    def validate_interview_schedule(self, interview_details: Dict[str, Any]) -> Dict[str, Any]:
        """Validate interview schedule details"""
        return self.scheduling_manager.validate_interview_schedule(interview_details)
    
    def process_candidate(self, candidate_data: CandidateData) -> Dict[str, Any]:
        """Process a candidate and provide scheduling recommendations"""
        try:
            # Get scheduling recommendation
            recommendation = self.scheduling_manager.get_scheduling_recommendation(candidate_data.score)
            
            # Generate AI insights
            prompt = f"""
            Analyze this candidate and provide comprehensive scheduling recommendations.
            
            Candidate: {candidate_data.name}
            Email: {candidate_data.email}
            Job Title: {candidate_data.job_title}
            Company: {candidate_data.company_name}
            Score: {candidate_data.score}/100
            
            Provide detailed recommendations for:
            1. Interview scheduling priority
            2. Recommended interview type and duration
            3. Email template selection
            4. Follow-up timeline
            5. Special considerations
            6. Next steps
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                'success': True,
                'candidate_data': candidate_data.model_dump(),
                'scheduling_recommendation': recommendation,
                'ai_insights': response.content,
                'suggested_templates': self._get_suggested_templates(candidate_data.score),
                'next_steps': self._get_next_steps(recommendation)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'processing_failed',
                'message': f'Error processing candidate: {str(e)}'
            }
    
    def _get_suggested_templates(self, score: int) -> List[str]:
        """Get suggested email templates based on score"""
        if score >= 70:
            return ["interview_invitation", "interview_confirmation"]
        else:
            return ["rejection"]
    
    def _get_next_steps(self, recommendation: Dict[str, Any]) -> List[str]:
        """Get next steps based on scheduling recommendation"""
        steps = []
        
        if recommendation.get('auto_schedule', False):
            steps.append("Schedule interview automatically")
            steps.append("Send interview invitation email")
            steps.append("Create calendar event")
        else:
            steps.append("Manual review required")
            steps.append("Send status update email")
        
        steps.append(f"Follow up within {recommendation.get('response_time', '48h')}")
        
        return steps
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'status': 'healthy',
            'config': self.config.get_config(),
            'email_templates_count': len(self.get_email_templates()),
            'calendar_enabled': self.config.calendar_enabled,
            'auto_send_emails': self.config.auto_send_emails
        }
