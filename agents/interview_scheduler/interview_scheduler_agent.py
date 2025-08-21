"""
Interview Scheduling Agent - LangGraph Implementation
Handles candidate scoring, email notifications, and calendar integration using LangGraph workflow
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()

class CandidateData(BaseModel):
    """Model for candidate data"""
    name: str = Field(description="Candidate's full name")
    email: str = Field(description="Candidate's email address")
    score: int = Field(description="Candidate's analysis score (0-100)")
    job_title: str = Field(description="Job title applied for")
    company_name: str = Field(description="Company name")
    resume_filename: str = Field(description="Resume file name")
    analysis_date: str = Field(description="Date of analysis")

class EmailTemplate(BaseModel):
    """Model for email templates"""
    subject: str
    body: str
    is_html: bool = True

class InterviewDetails(BaseModel):
    """Model for interview details"""
    interview_date: str
    interview_time: str
    meet_link: str
    confirmation_link: str
    duration: str = "45-60 minutes"
    format: str = "Video Interview via Google Meet"

class InterviewState(TypedDict):
    """State for interview scheduling workflow"""
    candidate_data: CandidateData
    candidate_status: str
    action_required: str
    email_template: Optional[EmailTemplate]
    interview_details: Optional[InterviewDetails]
    email_sent: bool
    success: bool
    message: str
    workflow_step: str

class LangGraphInterviewScheduler:
    """LangGraph-based Interview Scheduling Agent for HR Suite"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        self.company_name = os.getenv("COMPANY_NAME", "Your Company")
        self.hr_email = os.getenv("HR_EMAIL", "hr@company.com")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Email templates
        self.shortlisted_template = self._get_shortlisted_template()
        self.rejection_template = self._get_rejection_template()
        
        # Create LangGraph workflow
        self.workflow = self._create_workflow()
    
    def _get_shortlisted_template(self) -> EmailTemplate:
        """Get shortlisted email template"""
        return EmailTemplate(
            subject="Congratulations! You've Been Shortlisted for {job_title} Position",
            body="""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
                        🎉 Congratulations, {candidate_name}!
                    </h2>
                    
                    <p>We are pleased to inform you that your application for the <strong>{job_title}</strong> position at <strong>{company_name}</strong> has been shortlisted!</p>
                    
                    <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                        <h3 style="color: #155724; margin-top: 0;">📊 Your Analysis Score: {score}/100</h3>
                        <p style="margin-bottom: 0;">Your qualifications and experience align well with our requirements.</p>
                    </div>
                    
                    <h3 style="color: #2c3e50;">📅 Next Steps - Interview Scheduling</h3>
                    
                    <p>We would like to schedule an interview to discuss your application further. Here are the details:</p>
                    
                    <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin: 20px 0;">
                        <h4 style="color: #495057; margin-top: 0;">🎥 Interview Details:</h4>
                        <ul style="margin-bottom: 0;">
                            <li><strong>Format:</strong> Video Interview via Google Meet</li>
                            <li><strong>Duration:</strong> 45-60 minutes</li>
                            <li><strong>Date:</strong> {interview_date}</li>
                            <li><strong>Time:</strong> {interview_time}</li>
                            <li><strong>Meeting Link:</strong> <a href="{meet_link}" style="color: #3498db;">{meet_link}</a></li>
                        </ul>
                    </div>
                    
                    <h3 style="color: #2c3e50;">📋 What to Prepare:</h3>
                    <ul>
                        <li>Your portfolio or relevant work samples</li>
                        <li>Questions about the role and company</li>
                        <li>Reliable internet connection and quiet environment</li>
                        <li>Test your camera and microphone beforehand</li>
                    </ul>
                    
                    <h3 style="color: #2c3e50;">📧 Confirmation Required</h3>
                    <p>Please confirm your attendance by replying to this email or clicking the confirmation link below:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{confirmation_link}" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            ✅ Confirm Interview Attendance
                        </a>
                    </div>
                    
                    <p><strong>If you need to reschedule:</strong> Please contact us at least 24 hours before the scheduled time.</p>
                    
                    <div style="background-color: #e3f2fd; border: 1px solid #bbdefb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                        <h4 style="color: #1565c0; margin-top: 0;">💡 Interview Tips:</h4>
                        <ul style="margin-bottom: 0;">
                            <li>Research our company and recent news</li>
                            <li>Prepare specific examples of your achievements</li>
                            <li>Dress professionally as you would for an in-person interview</li>
                            <li>Have a backup plan in case of technical issues</li>
                        </ul>
                    </div>
                    
                    <p>We look forward to meeting you and learning more about your experience and how you can contribute to our team.</p>
                    
                    <p>Best regards,<br>
                    <strong>HR Team</strong><br>
                    {company_name}<br>
                    Email: {hr_email}</p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="font-size: 12px; color: #666;">
                        This email was sent automatically by our HR system. 
                        If you have any questions, please contact us at {hr_email}.
                    </p>
                </div>
            </body>
            </html>
            """
        )
    
    def _get_rejection_template(self) -> EmailTemplate:
        """Get rejection email template"""
        return EmailTemplate(
            subject="Application Status - {job_title} Position",
            body="""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px;">
                        Application Update
                    </h2>
                    
                    <p>Dear {candidate_name},</p>
                    
                    <p>Thank you for your interest in the <strong>{job_title}</strong> position at <strong>{company_name}</strong> and for taking the time to submit your application.</p>
                    
                    <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                        <h3 style="color: #721c24; margin-top: 0;">📊 Application Review</h3>
                        <p style="margin-bottom: 0;">After careful consideration of your application, we regret to inform you that we will not be moving forward with your candidacy at this time.</p>
                    </div>
                    
                    <h3 style="color: #2c3e50;">📈 Your Analysis Score: {score}/100</h3>
                    
                    <p>While your application demonstrated valuable experience, we have identified other candidates whose qualifications more closely align with our current requirements for this specific role.</p>
                    
                    <h3 style="color: #2c3e50;">💡 Moving Forward</h3>
                    
                    <p>We encourage you to:</p>
                    <ul>
                        <li>Continue developing your skills in relevant areas</li>
                        <li>Stay connected with our company for future opportunities</li>
                        <li>Apply for other positions that match your qualifications</li>
                        <li>Follow our careers page for new openings</li>
                    </ul>
                    
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                        <h4 style="color: #856404; margin-top: 0;">🌟 Future Opportunities</h4>
                        <p style="margin-bottom: 0;">
                            We maintain a database of qualified candidates and may reach out for future opportunities that better match your profile. 
                            We encourage you to keep your resume updated and continue applying for positions that interest you.
                        </p>
                    </div>
                    
                    <h3 style="color: #2c3e50;">📞 Feedback Request</h3>
                    <p>If you would like specific feedback about your application, please feel free to reach out to us at {hr_email}. We're happy to provide constructive feedback to help you in your job search.</p>
                    
                    <p>We appreciate your interest in joining our team and wish you the very best in your future endeavors.</p>
                    
                    <p>Best regards,<br>
                    <strong>HR Team</strong><br>
                    {company_name}<br>
                    Email: {hr_email}</p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="font-size: 12px; color: #666;">
                        This email was sent automatically by our HR system. 
                        If you have any questions, please contact us at {hr_email}.
                    </p>
                </div>
            </body>
            </html>
            """
        )
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for interview scheduling"""
        
        # Define workflow nodes
        def evaluate_candidate(state: InterviewState) -> InterviewState:
            """Evaluate candidate and determine next action"""
            candidate = state["candidate_data"]
            
            # Use LLM to evaluate candidate status
            evaluation_prompt = f"""
            Evaluate the candidate based on their score and provide a professional assessment.
            
            Candidate: {candidate.name}
            Job Title: {candidate.job_title}
            Score: {candidate.score}/100
            Company: {candidate.company_name}
            
            Based on the score, determine:
            1. Candidate status (Excellent Match, Strong Candidate, Shortlisted, Needs Review, Rejected)
            2. Recommended action (schedule_interview, send_rejection, needs_review)
            3. Professional reasoning
            
            Return a JSON response with: status, action, reasoning
            """
            
            response = self.llm.invoke([HumanMessage(content=evaluation_prompt)])
            
            try:
                evaluation = json.loads(response.content)
                state["candidate_status"] = evaluation.get("status", "Needs Review")
                state["action_required"] = evaluation.get("action", "needs_review")
                state["workflow_step"] = "evaluated"
                state["message"] = f"Candidate evaluated: {evaluation.get('reasoning', 'Score-based evaluation')}"
            except:
                # Fallback to score-based evaluation
                if candidate.score >= 80:
                    state["candidate_status"] = "Excellent Match"
                    state["action_required"] = "schedule_interview"
                elif candidate.score >= 70:
                    state["candidate_status"] = "Strong Candidate"
                    state["action_required"] = "schedule_interview"
                elif candidate.score >= 50:
                    state["candidate_status"] = "Shortlisted"
                    state["action_required"] = "schedule_interview"
                elif candidate.score >= 30:
                    state["candidate_status"] = "Needs Review"
                    state["action_required"] = "needs_review"
                else:
                    state["candidate_status"] = "Rejected"
                    state["action_required"] = "send_rejection"
                
                state["workflow_step"] = "evaluated"
                state["message"] = f"Candidate evaluated with score {candidate.score}/100"
            
            return state
        
        def prepare_interview_scheduling(state: InterviewState) -> InterviewState:
            """Prepare interview scheduling for shortlisted candidates"""
            if state["action_required"] != "schedule_interview":
                return state
            
            candidate = state["candidate_data"]
            
            # Use LLM to generate personalized interview details
            scheduling_prompt = f"""
            Generate personalized interview scheduling details for a shortlisted candidate.
            
            Candidate: {candidate.name}
            Job Title: {candidate.job_title}
            Score: {candidate.score}/100
            Status: {state["candidate_status"]}
            
            Create interview details including:
            1. Suggested interview date (next 3-5 business days)
            2. Suggested time slots (consider timezone)
            3. Meeting link format
            4. Confirmation link format
            
            Return a JSON response with: interview_date, interview_time, meet_link, confirmation_link
            """
            
            response = self.llm.invoke([HumanMessage(content=scheduling_prompt)])
            
            try:
                interview_data = json.loads(response.content)
                interview_details = InterviewDetails(
                    interview_date=interview_data.get("interview_date", "TBD"),
                    interview_time=interview_data.get("interview_time", "TBD"),
                    meet_link=interview_data.get("meet_link", "https://meet.google.com/xxx-xxxx-xxx"),
                    confirmation_link=interview_data.get("confirmation_link", "https://company.com/confirm/xxx")
                )
                state["interview_details"] = interview_details
                state["email_template"] = self.shortlisted_template
                state["workflow_step"] = "interview_scheduled"
                state["message"] = f"Interview scheduled for {candidate.name}"
            except:
                # Fallback to default scheduling
                interview_details = self._create_placeholder_interview(candidate.name, candidate.job_title)
                state["interview_details"] = interview_details
                state["email_template"] = self.shortlisted_template
                state["workflow_step"] = "interview_scheduled"
                state["message"] = f"Interview scheduled for {candidate.name}"
            
            return state
        
        def prepare_rejection(state: InterviewState) -> InterviewState:
            """Prepare rejection email for rejected candidates"""
            if state["action_required"] != "send_rejection":
                return state
            
            candidate = state["candidate_data"]
            
            # Use LLM to personalize rejection message
            rejection_prompt = f"""
            Generate a personalized rejection message for a candidate.
            
            Candidate: {candidate.name}
            Job Title: {candidate.job_title}
            Score: {candidate.score}/100
            Status: {state["candidate_status"]}
            
            Create a professional and encouraging rejection message that:
            1. Thanks the candidate for their interest
            2. Provides constructive feedback based on their score
            3. Encourages future applications
            4. Maintains positive company image
            
            Return a JSON response with: personalized_message
            """
            
            response = self.llm.invoke([HumanMessage(content=rejection_prompt)])
            
            try:
                rejection_data = json.loads(response.content)
                # Update rejection template with personalized message
                personalized_template = EmailTemplate(
                    subject=self.rejection_template.subject,
                    body=self.rejection_template.body.replace(
                        "While your application demonstrated valuable experience",
                        rejection_data.get("personalized_message", "While your application demonstrated valuable experience")
                    ),
                    is_html=True
                )
                state["email_template"] = personalized_template
                state["workflow_step"] = "rejection_prepared"
                state["message"] = f"Rejection prepared for {candidate.name}"
            except:
                state["email_template"] = self.rejection_template
                state["workflow_step"] = "rejection_prepared"
                state["message"] = f"Rejection prepared for {candidate.name}"
            
            return state
        
        def send_email(state: InterviewState) -> InterviewState:
            """Send email to candidate"""
            candidate = state["candidate_data"]
            email_template = state.get("email_template")
            interview_details = state.get("interview_details")
            
            if not email_template:
                state["email_sent"] = False
                state["success"] = False
                state["message"] = "No email template available"
                return state
            
            try:
                # Prepare email content
                subject = email_template.subject.format(
                    job_title=candidate.job_title
                )
                
                body = email_template.body.format(
                    candidate_name=candidate.name,
                    job_title=candidate.job_title,
                    company_name=candidate.company_name,
                    score=candidate.score,
                    interview_date=interview_details.interview_date if interview_details else "TBD",
                    interview_time=interview_details.interview_time if interview_details else "TBD",
                    meet_link=interview_details.meet_link if interview_details else "TBD",
                    confirmation_link=interview_details.confirmation_link if interview_details else "TBD",
                    hr_email=self.hr_email
                )
                
                # Send email
                email_sent = self._send_email(candidate.email, subject, body, True)
                state["email_sent"] = email_sent
                state["success"] = email_sent
                state["workflow_step"] = "email_sent"
                
                if email_sent:
                    state["message"] = f"Email sent successfully to {candidate.name}"
                else:
                    state["message"] = f"Failed to send email to {candidate.name}"
                
            except Exception as e:
                state["email_sent"] = False
                state["success"] = False
                state["message"] = f"Error sending email: {str(e)}"
            
            return state
        
        # Create workflow graph
        workflow = StateGraph(InterviewState)
        
        # Add nodes
        workflow.add_node("evaluate_candidate", evaluate_candidate)
        workflow.add_node("prepare_interview_scheduling", prepare_interview_scheduling)
        workflow.add_node("prepare_rejection", prepare_rejection)
        workflow.add_node("send_email", send_email)
        
        # Define edges
        workflow.set_entry_point("evaluate_candidate")
        
        # Conditional routing based on action required
        def route_after_evaluation(state: InterviewState) -> str:
            action = state["action_required"]
            if action == "schedule_interview":
                return "prepare_interview_scheduling"
            elif action == "send_rejection":
                return "prepare_rejection"
            else:
                return "send_email"  # For needs_review, send a generic email
        
        workflow.add_conditional_edges(
            "evaluate_candidate",
            route_after_evaluation,
            {
                "prepare_interview_scheduling": "prepare_interview_scheduling",
                "prepare_rejection": "prepare_rejection",
                "send_email": "send_email"
            }
        )
        
        # Continue to email sending
        workflow.add_edge("prepare_interview_scheduling", "send_email")
        workflow.add_edge("prepare_rejection", "send_email")
        
        # End workflow
        workflow.add_edge("send_email", END)
        
        return workflow.compile(checkpointer=MemorySaver())
    
    def _create_placeholder_interview(self, candidate_name: str, job_title: str) -> InterviewDetails:
        """Create placeholder interview details"""
        # Generate meeting ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = candidate_name.replace(' ', '').replace('-', '').replace('_', '')
        meeting_id = f"{safe_name}_{timestamp}"
        
        # Schedule for next business day
        tomorrow = datetime.now() + timedelta(days=1)
        interview_date = tomorrow.strftime("%A, %B %d, %Y")
        interview_time = "10:00 AM - 11:00 AM"
        
        return InterviewDetails(
            interview_date=interview_date,
            interview_time=interview_time,
            meet_link=f"https://meet.google.com/{meeting_id}",
            confirmation_link=f"https://{self.company_name.lower().replace(' ', '')}.com/confirm/{meeting_id}"
        )
    
    def _send_email(self, to_email: str, subject: str, body: str, is_html: bool = True) -> bool:
        """Send email using SMTP"""
        try:
            if not all([self.sender_email, self.sender_password]):
                raise Exception("SMTP credentials not configured")
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = to_email
            
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def process_candidate(self, candidate_data: CandidateData) -> Dict[str, Any]:
        """Process candidate using LangGraph workflow"""
        try:
            # Initialize state
            initial_state = InterviewState(
                candidate_data=candidate_data,
                candidate_status="",
                action_required="",
                email_template=None,
                interview_details=None,
                email_sent=False,
                success=False,
                message="",
                workflow_step="started"
            )
            
            # Execute workflow
            result = self.workflow.invoke(initial_state)
            
            # Extract final state
            final_state = result.get("__end__", result)
            
            return {
                'success': final_state.get("success", False),
                'action': final_state.get("action_required", ""),
                'email_sent': final_state.get("email_sent", False),
                'message': final_state.get("message", ""),
                'interview_details': final_state.get("interview_details", None),
                'candidate_status': final_state.get("candidate_status", ""),
                'workflow_steps': final_state.get("workflow_step", "")
            }
            
        except Exception as e:
            return {
                'success': False,
                'action': 'error',
                'email_sent': False,
                'message': f"Error processing candidate: {str(e)}",
                'interview_details': None,
                'candidate_status': "Error",
                'workflow_steps': "failed"
            }
    
    def get_candidate_status(self, score: int) -> str:
        """Get candidate status based on score"""
        if score >= 80:
            return "Excellent Match"
        elif score >= 70:
            return "Strong Candidate"
        elif score >= 50:
            return "Shortlisted"
        elif score >= 30:
            return "Needs Review"
        else:
            return "Rejected"
    
    def get_score_color(self, score: int) -> str:
        """Get color class based on score"""
        if score >= 80:
            return "success"
        elif score >= 70:
            return "info"
        elif score >= 50:
            return "warning"
        elif score >= 30:
            return "secondary"
        else:
            return "danger"

# Backward compatibility - keep the old class name
InterviewSchedulerAgent = LangGraphInterviewScheduler

def main():
    """Main function to test the LangGraph Interview Scheduler"""
    print("🤖 LangGraph Interview Scheduler Agent")
    print("=" * 50)
    
    # Initialize scheduler
    scheduler = LangGraphInterviewScheduler()
    
    # Test candidate data
    test_candidate = CandidateData(
        name="John Doe",
        email="john.doe@example.com",
        score=75,
        job_title="Software Developer",
        company_name="Tech Corp",
        resume_filename="john_doe_resume.pdf",
        analysis_date="2024-01-15"
    )
    
    # Process candidate
    result = scheduler.process_candidate(test_candidate)
    
    print(f"Processing Result: {result}")
    print("\n🎉 LangGraph Interview Scheduler is ready!")

if __name__ == "__main__":
    main()
