"""
Interview Scheduling Agent - Web UI
A Streamlit-based interface for processing candidates and sending emails
"""

import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from agents.interview_scheduler.interview_scheduler_agent import InterviewSchedulerAgent, CandidateData
from agents.root_agent.hr_root_agent import HRRootAgent

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Interview Scheduling Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #2c3e50;
        margin-bottom: 1.5rem;
        background: linear-gradient(90deg, #3498db, #2c3e50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .sub-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #34495e;
        margin-bottom: 1rem;
    }
    .score-display {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .high-score { 
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        color: #155724;
        border: 2px solid #28a745;
    }
    .medium-score { 
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        color: #856404;
        border: 2px solid #ffc107;
    }
    .low-score { 
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        color: #721c24;
        border: 2px solid #dc3545;
    }
    .action-button {
        padding: 15px 30px;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 10px;
        display: inline-block;
        text-decoration: none;
        text-align: center;
    }
    .shortlist-btn {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
    }
    .shortlist-btn:hover {
        background: linear-gradient(135deg, #218838, #1ea085);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(40, 167, 69, 0.3);
    }
    .reject-btn {
        background: linear-gradient(135deg, #dc3545, #e74c3c);
        color: white;
    }
    .reject-btn:hover {
        background: linear-gradient(135deg, #c82333, #c0392b);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(220, 53, 69, 0.3);
    }
    .candidate-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #3498db;
    }
    .status-badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    .status-shortlisted { background-color: #d4edda; color: #155724; }
    .status-rejected { background-color: #f8d7da; color: #721c24; }
    .status-pending { background-color: #fff3cd; color: #856404; }
    .email-preview {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        max-height: 300px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'scheduler_agent' not in st.session_state:
        st.session_state.scheduler_agent = None
    if 'root_agent' not in st.session_state:
        st.session_state.root_agent = None
    if 'candidates' not in st.session_state:
        st.session_state.candidates = []
    if 'selected_candidate' not in st.session_state:
        st.session_state.selected_candidate = None

def get_scheduler_agent():
    """Get or initialize the scheduler agent"""
    if st.session_state.scheduler_agent is None:
        try:
            st.session_state.scheduler_agent = InterviewSchedulerAgent()
        except Exception as e:
            st.error(f"Failed to initialize scheduler agent: {e}")
            return None
    return st.session_state.scheduler_agent

def get_root_agent():
    """Get or initialize the root agent"""
    if st.session_state.root_agent is None:
        try:
            st.session_state.root_agent = HRRootAgent()
        except Exception as e:
            st.error(f"Failed to initialize root agent: {e}")
            return None
    return st.session_state.root_agent

def get_score_color_class(score):
    """Get color class based on score"""
    if score >= 80:
        return "high-score"
    elif score >= 50:
        return "medium-score"
    else:
        return "low-score"

def load_candidates_from_analysis():
    """Load candidates from analysis results"""
    try:
        root_agent = get_root_agent()
        if root_agent is None:
            return []
        
        analysis_history = root_agent.get_analysis_history()
        candidates = []
        
        for analysis in analysis_history:
            data = analysis['data']
            metadata = data.get('metadata', {})
            
            # Extract candidate information
            candidate_name = metadata.get('candidate_name', 'Unknown')
            analysis_date = metadata.get('created_at', datetime.now().isoformat())
            
            # Get score
            overall_score = data.get('overall_score', 0)
            
            # Create candidate data
            candidate = {
                'name': candidate_name,
                'email': metadata.get('candidate_email', f"{candidate_name.lower().replace(' ', '.')}@example.com"),  # Use actual email from resume
                'score': overall_score,
                'job_title': 'Software Engineer',  # Placeholder - would come from analysis
                'company_name': 'Your Company',
                'resume_filename': f"{candidate_name}_resume.txt",
                'analysis_date': analysis_date,
                'status': 'pending',
                'analysis_data': data
            }
            
            candidates.append(candidate)
        
        return candidates
        
    except Exception as e:
        st.error(f"Error loading candidates: {e}")
        return []

def show_candidate_details(candidate):
    """Display candidate details and analysis"""
    st.markdown("### 📋 Candidate Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Name", candidate['name'])
        # Display email (read-only since it comes from resume)
        st.metric("Email", candidate['email'])
        # Allow editing if needed
        if st.checkbox("Edit Email Address", key=f"edit_email_{candidate['name']}"):
            candidate['email'] = st.text_input(
                "Email Address",
                value=candidate['email'],
                key=f"email_{candidate['name']}",
                help="Enter the candidate's actual email address"
            )
    
    with col2:
        st.metric("Job Title", candidate['job_title'])
        st.metric("Company", candidate['company_name'])
    
    with col3:
        st.metric("Analysis Date", candidate['analysis_date'][:10])
        status = candidate.get('status', 'pending')
        st.markdown(f"**Status:** <span class='status-badge status-{status}'>{status.title()}</span>", unsafe_allow_html=True)
    
    # Score display
    score = candidate['score']
    score_class = get_score_color_class(score)
    status_text = get_candidate_status_text(score)
    
    st.markdown(f"""
    <div class="score-display {score_class}">
        📊 Analysis Score: {score}/100<br>
        <small>{status_text}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Analysis breakdown
    if 'analysis_data' in candidate:
        analysis_data = candidate['analysis_data']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            skills_score = analysis_data.get('skills_analysis', {}).get('skill_match_percentage', 0)
            st.metric("Skills Match", f"{skills_score}%")
        
        with col2:
            experience_score = analysis_data.get('experience_analysis', {}).get('experience_score', 0)
            st.metric("Experience Score", f"{experience_score}/100")
        
        with col3:
            formatting_score = analysis_data.get('formatting_analysis', {}).get('overall_formatting_score', 0)
            st.metric("Formatting Score", f"{formatting_score}/100")

def get_candidate_status_text(score):
    """Get status text based on score"""
    if score >= 80:
        return "🎉 Excellent Match - Highly Recommended"
    elif score >= 70:
        return "👍 Strong Candidate - Recommended"
    elif score >= 50:
        return "✅ Shortlisted - Consider for Interview"
    elif score >= 30:
        return "🤔 Consider for Other Roles"
    else:
        return "❌ Not Suitable for This Position"

def show_action_buttons(candidate):
    """Show action buttons based on candidate score"""
    st.markdown("### 🎯 Take Action")
    
    score = candidate['score']
    
    if score >= 50:
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <h4 style="color: #28a745;">🎉 Candidate Qualifies for Interview!</h4>
            <p>This candidate has scored above the threshold and can be shortlisted for an interview.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ SHORTLIST CANDIDATE", type="primary", use_container_width=True):
                process_shortlist(candidate)
        
        with col2:
            if st.button("❌ REJECT CANDIDATE", type="secondary", use_container_width=True):
                process_rejection(candidate)
    
    else:
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <h4 style="color: #dc3545;">⚠️ Candidate Below Threshold</h4>
            <p>This candidate has scored below the minimum threshold for this position.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ OVERRIDE & SHORTLIST", type="secondary", use_container_width=True):
                process_shortlist(candidate)
        
        with col2:
            if st.button("❌ REJECT CANDIDATE", type="primary", use_container_width=True):
                process_rejection(candidate)

def process_shortlist(candidate):
    """Process shortlist action"""
    try:
        scheduler = get_scheduler_agent()
        if scheduler is None:
            st.error("Scheduler agent not available")
            return
        
        # Create candidate data
        candidate_data = CandidateData(
            name=candidate['name'],
            email=candidate['email'],
            score=candidate['score'],
            job_title=candidate['job_title'],
            company_name=candidate['company_name'],
            resume_filename=candidate['resume_filename'],
            analysis_date=candidate['analysis_date']
        )
        
        with st.spinner("📧 Sending shortlist email and scheduling interview..."):
            result = scheduler.process_candidate(candidate_data)
        
        if result['success']:
            st.success(f"✅ {result['message']}")
            
            # Show interview details
            if result['interview_details']:
                st.markdown("### 📅 Interview Details")
                details = result['interview_details']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Date:** {details['interview_date']}")
                    st.info(f"**Time:** {details['interview_time']}")
                
                with col2:
                    st.info(f"**Meeting Link:** {details['meet_link']}")
                    st.info(f"**Confirmation:** {details['confirmation_link']}")
            
            # Update candidate status
            candidate['status'] = 'shortlisted'
            
        else:
            st.error(f"❌ {result['message']}")
    
    except Exception as e:
        st.error(f"❌ Error processing shortlist: {str(e)}")

def process_rejection(candidate):
    """Process rejection action"""
    try:
        scheduler = get_scheduler_agent()
        if scheduler is None:
            st.error("Scheduler agent not available")
            return
        
        # Create candidate data
        candidate_data = CandidateData(
            name=candidate['name'],
            email=candidate['email'],
            score=candidate['score'],
            job_title=candidate['job_title'],
            company_name=candidate['company_name'],
            resume_filename=candidate['resume_filename'],
            analysis_date=candidate['analysis_date']
        )
        
        with st.spinner("📧 Sending rejection email..."):
            result = scheduler.process_candidate(candidate_data)
        
        if result['success']:
            st.success(f"✅ {result['message']}")
            # Update candidate status
            candidate['status'] = 'rejected'
        else:
            st.error(f"❌ {result['message']}")
    
    except Exception as e:
        st.error(f"❌ Error processing rejection: {str(e)}")

def show_email_preview(candidate, action):
    """Show email preview"""
    st.markdown("### 📧 Email Preview")
    
    scheduler = get_scheduler_agent()
    if scheduler is None:
        return
    
    if action == 'shortlist':
        template = scheduler.shortlisted_template
        interview_details = scheduler.schedule_interview(candidate['name'], candidate['job_title'])
        
        subject = template.subject.format(job_title=candidate['job_title'])
        body = template.body.format(
            candidate_name=candidate['name'],
            job_title=candidate['job_title'],
            company_name=candidate['company_name'],
            score=candidate['score'],
            interview_date=interview_details['interview_date'],
            interview_time=interview_details['interview_time'],
            meet_link=interview_details['meet_link'],
            confirmation_link=interview_details['confirmation_link'],
            hr_email=scheduler.hr_email
        )
    else:
        template = scheduler.rejection_template
        
        subject = template.subject.format(job_title=candidate['job_title'])
        body = template.body.format(
            candidate_name=candidate['name'],
            job_title=candidate['job_title'],
            company_name=candidate['company_name'],
            score=candidate['score'],
            hr_email=scheduler.hr_email
        )
    
    st.markdown(f"**Subject:** {subject}")
    st.markdown(f"**To:** {candidate['email']}")
    
    st.markdown("**Body Preview:**")
    st.markdown(f"""
    <div class="email-preview">
        {body[:500]}...
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Main header
    st.markdown('<h1 class="main-header">📧 Interview Scheduling Agent</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Candidate Processing & Email Automation")
    
    # Description
    st.markdown("""
    This agent processes candidate analysis results and automatically sends appropriate emails based on their scores.
    - **Scores ≥ 50**: Automatically shortlisted with interview scheduling and Google Meet integration
    - **Scores < 50**: Rejection emails with constructive feedback
    - **Professional email templates** with company branding
    - **Calendar integration** for interview scheduling
    """)
    
    # Load candidates
    if not st.session_state.candidates:
        st.session_state.candidates = load_candidates_from_analysis()
    
    # Sidebar for candidate selection
    st.sidebar.title("👥 Candidates")
    
    if st.session_state.candidates:
        candidate_names = [f"{c['name']} ({c['score']}/100)" for c in st.session_state.candidates]
        selected_index = st.sidebar.selectbox(
            "Select a candidate:",
            range(len(st.session_state.candidates)),
            format_func=lambda x: candidate_names[x]
        )
        
        if selected_index is not None:
            selected_candidate = st.session_state.candidates[selected_index]
            st.session_state.selected_candidate = selected_candidate
            
            # Main content area
            if st.session_state.selected_candidate:
                candidate = st.session_state.selected_candidate
                
                # Show candidate details
                show_candidate_details(candidate)
                
                # Show action buttons
                show_action_buttons(candidate)
                
                # Email preview section
                st.markdown("---")
                action = st.radio(
                    "Preview Email Template:",
                    ["Shortlisted Email", "Rejection Email"],
                    horizontal=True
                )
                
                if action == "Shortlisted Email":
                    show_email_preview(candidate, 'shortlist')
                else:
                    show_email_preview(candidate, 'rejection')
    
    else:
        st.warning("⚠️ No candidates found!")
        st.info("""
        **To get started:**
        1. Use the Resume Analyzer to analyze candidate resumes
        2. Return here to process the analysis results
        3. Send appropriate emails based on scores
        """)
        
        if st.button("🔄 Refresh Candidates"):
            st.session_state.candidates = load_candidates_from_analysis()
            st.rerun()
    
    # Configuration section
    with st.sidebar.expander("⚙️ Configuration"):
        st.markdown("**Email Settings:**")
        st.info("Configure SMTP settings in your `.env` file:")
        st.code("""
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
COMPANY_NAME=Your Company Name
HR_EMAIL=hr@yourcompany.com
        """)
        
        st.markdown("**Score Thresholds:**")
        st.info("""
        - **≥ 80**: Excellent Match
        - **≥ 70**: Strong Candidate  
        - **≥ 50**: Shortlisted
        - **≥ 30**: Consider for Other Roles
        - **< 30**: Not Suitable
        """)

if __name__ == "__main__":
    main()
