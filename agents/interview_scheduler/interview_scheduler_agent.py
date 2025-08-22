"""
Interview Scheduling Agent - Simple Implementation
Handles candidate scoring, email notifications, and interview scheduling
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

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

class InterviewSchedulerAgent:
    """Simple Interview Scheduling Agent for HR Suite"""
    
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
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #28a745; margin-top: 0;">📊 Your Analysis Score: {score}/100</h3>
                        <p>Your profile has demonstrated excellent alignment with our requirements and company culture.</p>
                    </div>
                    
                    <h3 style="color: #2c3e50;">📅 Interview Details</h3>
                    <div style="background-color: #e8f4fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                        <p><strong>Date:</strong> {interview_date}</p>
                        <p><strong>Time:</strong> {interview_time}</p>
                        <p><strong>Duration:</strong> {duration}</p>
                        <p><strong>Format:</strong> {format}</p>
                        <p><strong>Meeting Link:</strong> <a href="{meet_link}" style="color: #3498db;">{meet_link}</a></p>
                    </div>
                    
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                        <h4 style="color: #856404; margin-top: 0;">💡 What to Prepare</h4>
                        <ul>
                            <li>Review the job description and your resume</li>
                            <li>Prepare questions about the role and company</li>
                            <li>Test your video conferencing setup</li>
                            <li>Find a quiet, well-lit environment</li>
                        </ul>
                    </div>
                    
                    <p><strong>Please confirm your attendance by clicking:</strong> <a href="{confirmation_link}" style="color: #3498db; font-weight: bold;">Confirm Interview</a></p>
                    
                    <p>If you need to reschedule or have any questions, please contact us at <a href="mailto:{hr_email}" style="color: #3498db;">{hr_email}</a>.</p>
                    
                    <p>We look forward to meeting you!</p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                        <p style="color: #6c757d; font-size: 0.9em;">
                            Best regards,<br>
                            <strong>HR Team</strong><br>
                            {company_name}
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
        )
    
    def _get_rejection_template(self) -> EmailTemplate:
        """Get rejection email template"""
        return EmailTemplate(
            subject="Application Update - {job_title} Position",
            body="""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px;">
                        Application Update
                    </h2>
                    
                    <p>Dear {candidate_name},</p>
                    
                    <p>Thank you for your interest in the <strong>{job_title}</strong> position at <strong>{company_name}</strong> and for taking the time to submit your application.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #6c757d; margin-top: 0;">📊 Your Analysis Score: {score}/100</h3>
                        <p>We have carefully reviewed your application and conducted a thorough analysis of your profile.</p>
                    </div>
                    
                    <p>After careful consideration, we regret to inform you that we will not be moving forward with your application at this time. This decision was based on our current requirements and the specific needs of the position.</p>
                    
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                        <h4 style="color: #856404; margin-top: 0;">💡 Keep in Touch</h4>
                        <p>We encourage you to:</p>
                        <ul>
                            <li>Apply for future positions that match your skills</li>
                            <li>Follow our company for updates on new opportunities</li>
                            <li>Continue developing your professional skills</li>
                        </ul>
                    </div>
                    
                    <p>We appreciate your interest in joining our team and wish you the best in your future endeavors.</p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                        <p style="color: #6c757d; font-size: 0.9em;">
                            Best regards,<br>
                            <strong>HR Team</strong><br>
                            {company_name}<br>
                            <a href="mailto:{hr_email}" style="color: #3498db;">{hr_email}</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
        )
    
    def _create_placeholder_interview(self, candidate_name: str, job_title: str) -> InterviewDetails:
        """Create placeholder interview details"""
        # Schedule interview for next business day at 2 PM
        tomorrow = datetime.now() + timedelta(days=1)
        if tomorrow.weekday() >= 5:  # Saturday or Sunday
            tomorrow += timedelta(days=2 if tomorrow.weekday() == 5 else 1)  # Move to Monday
        
        interview_date = tomorrow.strftime("%A, %B %d, %Y")
        interview_time = "2:00 PM - 3:00 PM"
        
        # Create Google Meet link
        meet_link = f"https://meet.google.com/{self._generate_meet_code()}"
        confirmation_link = f"https://calendly.com/{self.company_name.lower().replace(' ', '')}/interview-confirmation"
        
        return InterviewDetails(
            interview_date=interview_date,
            interview_time=interview_time,
            meet_link=meet_link,
            confirmation_link=confirmation_link
        )
    
    def _generate_meet_code(self) -> str:
        """Generate a random Google Meet code"""
        import random
        import string
        # Generate a 3-letter, 4-digit, 3-letter code (e.g., abc-1234-def)
        letters = ''.join(random.choices(string.ascii_lowercase, k=3))
        digits = ''.join(random.choices(string.digits, k=4))
        letters2 = ''.join(random.choices(string.ascii_lowercase, k=3))
        return f"{letters}-{digits}-{letters2}"
    
    def _send_email(self, to_email: str, subject: str, body: str, is_html: bool = True) -> bool:
        """Send email using SMTP"""
        try:
            if not self.sender_email or not self.sender_password:
                print("⚠️ SMTP credentials not configured. Email not sent.")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
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
            print(f"❌ Error sending email: {str(e)}")
            return False
    
    def _process_shortlist(self, candidate_data: CandidateData) -> Dict[str, Any]:
        """Process shortlisted candidate"""
        try:
            # Create interview details
            interview_details = self._create_placeholder_interview(
                candidate_data.name, 
                candidate_data.job_title
            )
            
            # Prepare email
            subject = self.shortlisted_template.subject.format(
                job_title=candidate_data.job_title
            )
            
            body = self.shortlisted_template.body.format(
                candidate_name=candidate_data.name,
                job_title=candidate_data.job_title,
                company_name=candidate_data.company_name,
                score=candidate_data.score,
                interview_date=interview_details.interview_date,
                interview_time=interview_details.interview_time,
                meet_link=interview_details.meet_link,
                confirmation_link=interview_details.confirmation_link,
                duration=interview_details.duration,
                format=interview_details.format,
                hr_email=self.hr_email
            )
            
            # Send email
            email_sent = self._send_email(
                candidate_data.email, 
                subject, 
                body, 
                is_html=True
            )
            
            if email_sent:
                return {
                    'success': True,
                    'message': f"Shortlist email sent successfully to {candidate_data.name}",
                    'interview_details': interview_details.dict()
                }
            else:
                return {
                    'success': False,
                    'message': f"Failed to send shortlist email to {candidate_data.name}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Error processing shortlist: {str(e)}"
            }
    
    def _process_rejection(self, candidate_data: CandidateData) -> Dict[str, Any]:
        """Process rejected candidate"""
        try:
            # Prepare email
            subject = self.rejection_template.subject.format(
                job_title=candidate_data.job_title
            )
            
            body = self.rejection_template.body.format(
                candidate_name=candidate_data.name,
                job_title=candidate_data.job_title,
                company_name=candidate_data.company_name,
                score=candidate_data.score,
                hr_email=self.hr_email
            )
            
            # Send email
            email_sent = self._send_email(
                candidate_data.email, 
                subject, 
                body, 
                is_html=True
            )
            
            if email_sent:
                return {
                    'success': True,
                    'message': f"Rejection email sent successfully to {candidate_data.name}"
                }
            else:
                return {
                    'success': False,
                    'message': f"Failed to send rejection email to {candidate_data.name}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Error processing rejection: {str(e)}"
            }
    
    def process_candidate(self, candidate_data: CandidateData) -> Dict[str, Any]:
        """Process candidate based on score"""
        try:
            # Determine action based on score
            if candidate_data.score >= 50:
                # Shortlist candidate
                return self._process_shortlist(candidate_data)
            else:
                # Reject candidate
                return self._process_rejection(candidate_data)
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Error processing candidate: {str(e)}"
            }
    
    def process_candidate_with_data(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process candidate with dict data input"""
        try:
            # Convert dict to CandidateData object
            candidate_obj = CandidateData(**candidate_data)
            
            # Process candidate
            return self.process_candidate(candidate_obj)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process candidate for interview'
            }
    
    def get_interview_details_for_preview(self, candidate_name: str, job_title: str) -> InterviewDetails:
        """Get interview details for email preview"""
        return self._create_placeholder_interview(candidate_name, job_title)

def main():
    """Main function to test the Interview Scheduler"""
    print("🤖 Interview Scheduler Agent")
    print("=" * 50)
    
    # Test the scheduler
    scheduler = InterviewSchedulerAgent()
    
    # Test candidate data
    test_candidate = CandidateData(
        name="John Doe",
        email="john.doe@example.com",
        score=75,
        job_title="Software Engineer",
        company_name="Tech Corp",
        resume_filename="john_doe_resume.pdf",
        analysis_date="2024-01-15"
    )
    
    print(f"📧 Testing with candidate: {test_candidate.name}")
    print(f"📊 Score: {test_candidate.score}/100")
    
    # Process candidate
    result = scheduler.process_candidate(test_candidate)
    
    print(f"✅ Result: {result['success']}")
    print(f"📝 Message: {result['message']}")
    
    if result['success'] and 'interview_details' in result:
        details = result['interview_details']
        print(f"📅 Interview Date: {details['interview_date']}")
        print(f"⏰ Interview Time: {details['interview_time']}")
        print(f"🔗 Meet Link: {details['meet_link']}")
    
    print("\n🎉 Interview Scheduler is ready!")

if __name__ == "__main__":
    main()
