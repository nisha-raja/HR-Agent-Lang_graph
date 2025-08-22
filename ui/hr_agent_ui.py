"""
HR Agent Suite - Web UI
A Streamlit-based web interface using the root agent for coordination
"""

import streamlit as st
import os
import sys
import re
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from agents.root_agent.hr_root_agent import HRRootAgent
from utils.config_manager import ConfigManager
from utils.file_manager import FileManager
import PyPDF2
import docx
from PIL import Image
import pytesseract

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Clear session state to force fresh initialization (add this after imports)
if 'scheduler_agent' in st.session_state:
    del st.session_state.scheduler_agent
if 'root_agent' in st.session_state:
    del st.session_state.root_agent

# Check for any LangGraph imports that might be causing issues
# try:
#     import langgraph
#     st.warning("⚠️ LangGraph is still imported. This might cause issues.")
# except ImportError:
#     pass  # Good, LangGraph is not imported

# Page configuration - only set if not already set
if not hasattr(st, '_page_config_set'):
    st.set_page_config(
        page_title="HR Agent Suite",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st._page_config_set = True

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .score-display {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .high-score { background-color: #d4edda; color: #155724; }
    .medium-score { background-color: #fff3cd; color: #856404; }
    .low-score { background-color: #f8d7da; color: #721c24; }
    .upload-area {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f9f9f9;
        margin: 1rem 0;
    }
    .upload-area:hover {
        border-color: #1f77b4;
        background-color: #f0f8ff;
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
    .root-agent-icon {
        font-size: 3rem;
        cursor: pointer;
        text-align: center;
        padding: 1rem;
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        background-color: #f0f8ff;
        transition: all 0.3s ease;
    }
    .root-agent-icon:hover {
        background-color: #e6f3ff;
        border-color: #0056b3;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'root_agent' not in st.session_state:
        st.session_state.root_agent = None
    if 'jd_generated' not in st.session_state:
        st.session_state.jd_generated = False
    if 'jd_content' not in st.session_state:
        st.session_state.jd_content = ""
    if 'jd_metadata' not in st.session_state:
        st.session_state.jd_metadata = {}
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    # Add these new session state variables
    if 'show_root_agent_input' not in st.session_state:
        st.session_state.show_root_agent_input = False
    if 'parsed_job_details' not in st.session_state:
        st.session_state.parsed_job_details = {}

def get_root_agent():
    """Get or initialize the root agent"""
    if st.session_state.root_agent is None:
        try:
            st.session_state.root_agent = HRRootAgent()
        except Exception as e:
            st.error(f"Failed to initialize root agent: {e}")
            return None
    return st.session_state.root_agent

def get_scheduler_agent():
    """Get or initialize the scheduler agent"""
    if st.session_state.scheduler_agent is None:
        try:
            # Force fresh import to avoid caching issues
            import importlib
            import agents.interview_scheduler.interview_scheduler_agent as scheduler_module
            importlib.reload(scheduler_module)
            
            from agents.interview_scheduler.interview_scheduler_agent import InterviewSchedulerAgent
            st.session_state.scheduler_agent = InterviewSchedulerAgent()
            
        except Exception as e:
            st.error(f"Failed to initialize scheduler agent: {e}")
            return None
    return st.session_state.scheduler_agent

def get_score_color(score):
    """Get color class based on score"""
    if score >= 80:
        return "high-score"
    elif score >= 60:
        return "medium-score"
    else:
        return "low-score"

def extract_candidate_name(resume_content):
    """Extract candidate name from resume content"""
    try:
        lines = resume_content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) > 2 and len(line) < 50:  # Reasonable name length
                # Skip common resume headers
                skip_words = ['resume', 'cv', 'curriculum vitae', 'phone', 'email', 'address', 'objective', 'summary']
                if not any(skip_word in line.lower() for skip_word in skip_words):
                    # Check if line looks like a name (contains letters and possibly spaces)
                    if line.replace(' ', '').replace('-', '').replace('.', '').isalpha():
                        return line
        return "Unknown Candidate"
    except:
        return "Unknown Candidate"

def extract_candidate_email(resume_content):
    """Extract candidate email from resume content"""
    try:
        import re
        # Enhanced email regex pattern to catch more email formats
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, resume_content)
        
        if emails:
            # Filter out common non-personal emails and return the first valid one
            for email in emails:
                email_lower = email.lower()
                # Skip common non-personal email patterns
                if any(skip in email_lower for skip in ['example.com', 'test.com', 'sample.com', 'placeholder']):
                    continue
                # Return the first valid personal email
                return email
            
            # If all emails were filtered out, return the first one anyway
            return emails[0] if emails else None
        else:
            return None
    except Exception as e:
        st.error(f"Error extracting email: {e}")
        return None

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file (PDF, DOCX, TXT, JPEG, JPG)"""
    try:
        file_extension = uploaded_file.name.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            # Handle PDF files
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        
        elif file_extension == 'docx':
            # Handle DOCX files
            doc = docx.Document(uploaded_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        
        elif file_extension == 'txt':
            # Handle TXT files
            return uploaded_file.getvalue().decode('utf-8').strip()
        
        elif file_extension in ['jpg', 'jpeg']:
            # Handle JPEG/JPG image files using OCR
            try:
                # Check if tesseract is available
                try:
                    pytesseract.get_tesseract_version()
                except Exception as e:
                    st.error("❌ Tesseract OCR is not accessible!")
                    st.info(f"""
                    **Error:** {str(e)}
                    
                    **Solutions:**
                    1. **Restart your terminal/VS Code** (PATH changes need a fresh session)
                    2. **Verify Tesseract is installed** at: `C:\\Program Files\\Tesseract-OCR`
                    3. **Check PATH variable** includes: `C:\\Program Files\\Tesseract-OCR`
                    
                    **Alternative:** Convert your image to PDF/DOCX format for now.
                    """)
                    return None
                
                # Open the image
                image = Image.open(uploaded_file)
                
                # Use pytesseract to extract text
                text = pytesseract.image_to_string(image)
                
                if not text.strip():
                    st.warning("⚠️ No text could be extracted from the image. Please ensure the image is clear and contains readable text.")
                    return None
                
                return text.strip()
                
            except Exception as ocr_error:
                st.error(f"❌ Error processing image with OCR: {str(ocr_error)}")
                st.info("💡 Make sure the image is clear, well-lit, and contains readable text.")
                return None
        
        else:
            st.error(f"❌ Unsupported file format: {file_extension}")
            st.info("Supported formats: PDF, DOCX, TXT, JPG, JPEG")
            return None
            
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        return None

def parse_job_details_from_text(text, root_agent):
    """Parse job details from natural language text using LLM - Fully dynamic approach"""
    try:
        # Create a comprehensive prompt for the LLM to analyze and extract ALL information
        prompt = f"""
        Analyze the following job description text and extract ALL relevant information. 
        Return ONLY a JSON object with the extracted information.
        
        Job description text: "{text}"
        
        Instructions:
        1. Extract ALL job-related information from the text
        2. Include standard fields: job_title, experience_required, salary_range, employment_type, location, industry, department, company_name
        3. If any standard field is NOT mentioned in the text, set it to empty string ""
        4. If you find additional important information not covered by standard fields, create new fields for them
        5. Examples of additional fields you might create:
           - visa_required: "Yes/No/Not specified"
           - education_required: "Bachelor's/Master's/PhD/etc"
           - skills_required: "list of required skills"
           - certifications: "required certifications"
           - shift_type: "Day/Night/Rotating"
           - travel_required: "Yes/No"
           - remote_work: "Yes/No/Hybrid"
           - benefits: "health insurance, etc"
           - any other relevant job details
        
        6. For industry: Analyze the profession and determine the appropriate industry
        7. For department: Analyze the role and determine the appropriate department
        8. Do NOT add default values unless they are explicitly mentioned in the text
        9. Always return valid JSON
        
        10. **CRITICAL: Correct ALL spelling mistakes automatically**
            Examples of spelling corrections:
            - "dactor" → "doctor"
            - "surgen" → "surgeon"
            - "engeneer" → "engineer"
            - "develper" → "developer"
            - "progrmmer" → "programmer"
            - "maneger" → "manager"
            - "techer" → "teacher"
            - **Use your intelligence to correct ANY other spelling mistakes you encounter**
            - **Always provide the most appropriate and professional job title**
        
        Return format:
        {{
            "job_title": "extracted or inferred job title (with spelling corrections)",
            "experience_required": "experience requirement or empty string",
            "salary_range": "salary if mentioned or empty string",
            "employment_type": "employment type if mentioned or empty string",
            "location": "location if mentioned or empty string",
            "industry": "inferred industry based on profession",
            "department": "inferred department based on role",
            "company_name": "Your Company",
            "visa_required": "Yes/No/Not specified based on text",
            "education_required": "education requirement if mentioned (with spelling corrections)",
            "skills_required": "required skills if mentioned (with spelling corrections)",
            "certifications": "certifications if mentioned (with spelling corrections)",
            "shift_type": "shift information if mentioned (with spelling corrections)",
            "travel_required": "travel requirement if mentioned",
            "remote_work": "remote work policy if mentioned",
            "benefits": "benefits if mentioned (with spelling corrections)",
            "additional_notes": "any other important details (with spelling corrections)"
        }}
        
        IMPORTANT: 
        - Only include fields that have actual information from the text. If a field is not mentioned, either omit it or set it to empty string.
        - Always correct spelling mistakes to proper English
        - Use proper job titles and professional terminology
        - Be intelligent about context - if someone writes "dactor" they likely mean "doctor"
        """
        
        # Use the LLM from the JD generator agent
        from agents.jd_generator.jd_generator_agent import LangGraphJDGenerator
        jd_generator = LangGraphJDGenerator()
        
        # Create a simple message for the LLM
        from langchain_core.messages import HumanMessage
        
        response = jd_generator.llm.invoke([HumanMessage(content=prompt)])
        
        # Parse the JSON response
        import json
        try:
            parsed = json.loads(response.content)
            
            # Clean up the parsed data - ensure empty strings instead of None
            for key, value in parsed.items():
                if value is None:
                    parsed[key] = ""
                    
            return parsed
            
        except json.JSONDecodeError:
            # Fallback to regex if LLM response is not valid JSON
            st.warning("⚠️ LLM parsing failed, using fallback method")
            return parse_job_details_fallback(text)
            
    except Exception as e:
        st.error(f"❌ Error parsing with LLM: {str(e)}")
        # Fallback to regex method
        return parse_job_details_fallback(text)

def parse_job_details_fallback(text):
    """Fallback regex-based parsing if LLM fails"""
    # Simplified fallback that just extracts basic info
    text = text.lower().strip()
    parsed = {}
    
    # Basic extraction for fallback
    parsed['job_title'] = 'Professional'
    parsed['experience_required'] = ''
    parsed['salary_range'] = ''
    parsed['employment_type'] = ''
    parsed['location'] = ''
    parsed['industry'] = ''
    parsed['department'] = ''
    parsed['company_name'] = 'Your Company'
    
    return parsed

def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Main header
    st.markdown('<h1 class="main-header">🤖 HR Agent Suite</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Job Description Generator & Resume Analyzer")
    
    # Workflow Navigation
    st.markdown("### 🔄 **Complete HR Workflow**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **1️⃣ Job Description Generator**
        - Create professional job descriptions
        - AI-powered content generation
        """)
        if st.button("📝 Start JD Generation", type="primary", use_container_width=True):
            st.session_state.current_page = "JD Generator"
            st.rerun()
    
    with col2:
        st.markdown("""
        **2️⃣ Resume Analyzer**
        - Analyze resumes against JDs
        - Extract candidate info & scores
        """)
        if st.button("🔍 Start Resume Analysis", type="primary", use_container_width=True):
            st.session_state.current_page = "Resume Analyzer"
            st.rerun()
    
    with col3:
        st.markdown("""
        **3️⃣ Interview Scheduler**
        - Process candidates by score
        - Send automated emails
        """)
        if st.button("📧 Start Interview Scheduling", type="primary", use_container_width=True):
            st.session_state.current_page = "Interview Scheduler"
            st.rerun()
    
    st.markdown("---")
    
    # Initialize root agent
    root_agent = get_root_agent()
    if root_agent is None:
        st.error("❌ Failed to initialize HR Agent Suite. Please check your configuration.")
        return
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choose a page:",
        ["🏠 Home", "📝 Generate Job Description", "📊 Analyze Resume", "📧 Interview Scheduler", "📋 View Results", "🔧 System Status"]
    )
    
    if page == "🏠 Home":
        show_home_page(root_agent)
    elif page == "📝 Generate Job Description":
        show_jd_generator(root_agent)
    elif page == "📊 Analyze Resume":
        show_resume_analyzer(root_agent)
    elif page == "📧 Interview Scheduler":
        show_interview_scheduler(root_agent)
    elif page == "📋 View Results":
        show_results()
    elif page == "🔧 System Status":
        show_system_status(root_agent)

def show_home_page(root_agent):
    """Display home page with overview"""
    st.markdown('<h2 class="sub-header">Welcome to HR Agent Suite</h2>', unsafe_allow_html=True)
    
    # Get system status
    status = root_agent.get_system_status()
    
    # Quick Access to Individual Tools
    st.markdown("### 🛠️ **Individual Tools**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 Job Description Generator**
        - Create professional job descriptions
        - AI-powered content generation
        """)
        
        if st.button("📝 Generate JD", type="secondary"):
            st.session_state.current_page = "JD Generator"
            st.rerun()
    
    with col2:
        st.markdown("""
        **📊 Resume Analyzer**
        - Evaluate resumes against job descriptions
        - Extract candidate information automatically
        """)
        
        if st.button("🔍 Analyze Resume", type="secondary"):
            st.session_state.current_page = "Resume Analyzer"
            st.rerun()
    
    # System status
    st.markdown("---")
    st.markdown("### 🔧 System Status")
    
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.metric("System Status", status['status'].title())
    
    with status_col2:
        job_descriptions = root_agent.get_available_job_descriptions()
        st.metric("Job Descriptions", len(job_descriptions))
    
    with status_col3:
        analysis_history = root_agent.get_analysis_history()
        st.metric("Analysis Results", len(analysis_history))

def show_jd_generator(root_agent):
    """Job Description Generator Page with Dynamic LLM-Driven Form"""
    st.markdown('<h2 class="sub-header">📝 Job Description Generator</h2>', unsafe_allow_html=True)
    
    # Root Agent Quick Input Section
    st.markdown("### 🤖 Root Agent Quick Input")
    st.markdown("**💡 Tip:** Click the Root Agent icon below to quickly enter job details in natural language!")
    
    # Root Agent Icon and Input
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🤖", help="Click to open Root Agent input", key="root_agent_icon", use_container_width=True):
            st.session_state.show_root_agent_input = True
    
    # Root Agent Text Input
    if st.session_state.get('show_root_agent_input', False):
        st.markdown("#### 🎯 Enter Job Details (Natural Language)")
        st.markdown("**Example:** `doctor, 50000 salary, 8 year experience, surgeon, ENT, General, visa required, master degree, night shift`")
        
        job_details_text = st.text_area(
            "Job Details:",
            placeholder="Enter job details in natural language...",
            height=100,
            key="root_agent_input"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Parse & Pre-fill", type="primary"):
                if job_details_text.strip():
                    parsed_details = parse_job_details_from_text(job_details_text, root_agent)
                    st.session_state.parsed_job_details = parsed_details
                    st.session_state.show_root_agent_input = False
                    st.success("✅ Job details parsed successfully! Form pre-filled below.")
                    st.rerun()
                else:
                    st.error("Please enter job details.")
        
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.show_root_agent_input = False
                st.rerun()
    
    # Dynamic Form Generation based on LLM Response
    with st.form("jd_generator_form"):
        st.markdown("### 📋 Job Details")
        
        # Pre-fill form if we have parsed details
        parsed_details = st.session_state.get('parsed_job_details', {})
        
        # Standard fields in two columns
        col1, col2 = st.columns(2)
        
        with col1:
            # First column - capture values directly
            job_title = st.text_input(
                'Job Title *',
                value=parsed_details.get('job_title', ''),
                placeholder='e.g., Senior Software Engineer',
                key="form_job_title"
            )
            
            company_name = st.text_input(
                'Company Name *',
                value=parsed_details.get('company_name', ''),
                placeholder='e.g., TechCorp Inc.',
                key="form_company_name"
            )
            
            experience_required = st.text_input(
                'Experience Required *',
                value=parsed_details.get('experience_required', ''),
                placeholder='e.g., 5+ years',
                key="form_experience_required"
            )
            
            # Employment type dropdown
            employment_options = ['Full-time', 'Part-time', 'Contract', 'Internship']
            employment_index = 0
            if parsed_details.get('employment_type'):
                try:
                    employment_index = employment_options.index(parsed_details['employment_type'])
                except ValueError:
                    employment_index = 0
            
            employment_type = st.selectbox(
                'Employment Type *',
                employment_options,
                index=employment_index,
                key="form_employment_type"
            )
        
        with col2:
            # Second column - capture values directly
            salary_range = st.text_input(
                'Salary Range *',
                value=parsed_details.get('salary_range', ''),
                placeholder='e.g., $80,000 - $100,000',
                key="form_salary_range"
            )
            
            industry = st.text_input(
                'Industry',
                value=parsed_details.get('industry', ''),
                placeholder='e.g., Technology',
                key="form_industry"
            )
            
            location = st.text_input(
                'Location',
                value=parsed_details.get('location', ''),
                placeholder='e.g., Remote',
                key="form_location"
            )
            
            department = st.text_input(
                'Department',
                value=parsed_details.get('department', ''),
                placeholder='e.g., Engineering',
                key="form_department"
            )
        
        # Dynamic fields based on LLM response
        dynamic_form_data = {}
        for key, value in parsed_details.items():
            if key not in ['job_title', 'company_name', 'experience_required', 'employment_type', 
                          'salary_range', 'industry', 'location', 'department'] and value:
                field_label = key.replace('_', ' ').title()
                
                if isinstance(value, str):
                    if value.lower() in ['yes', 'no', 'not specified']:
                        # Boolean/choice field
                        options = ['Not specified', 'Yes', 'No']
                        index = 0
                        try:
                            index = options.index(value)
                        except ValueError:
                            index = 0
                        dynamic_form_data[key] = st.selectbox(
                            field_label,
                            options,
                            index=index,
                            key=f"form_{key}"
                        )
                    else:
                        # Text field
                        dynamic_form_data[key] = st.text_input(
                            field_label,
                            value=value,
                            placeholder=f"Enter {field_label.lower()}",
                            key=f"form_{key}"
                        )
        
        submitted = st.form_submit_button("🚀 Generate Job Description", type="primary")
        
        if submitted:
            # Collect all form data from actual form inputs
            form_data = {
                'job_title': job_title.strip(),
                'company_name': company_name.strip(),
                'experience_required': experience_required.strip(),
                'employment_type': employment_type,
                'salary_range': salary_range.strip(),
                'industry': industry.strip(),
                'location': location.strip(),
                'department': department.strip()
            }
            
            # Add dynamic fields
            form_data.update(dynamic_form_data)
            
            # Process form submission using JD Generator Agent
            with st.spinner("🤖 Generating job description..."):
                result = root_agent.jd_generator.process_form_submission(form_data)
                
                if result['success']:
                    # Save to session state
                    st.session_state.jd_generated = True
                    st.session_state.jd_content = result['job_description']
                    st.session_state.jd_metadata = result['job_details']
                    st.success("✅ Job description generated successfully!")
                    
                    # Display the generated JD immediately
                    st.markdown("### Generated Job Description")
                    st.text_area("Job Description", result['job_description'], height=400, disabled=True)
                    
                else:
                    if result['error'] == 'validation_failed':
                        st.error(f"❌ {result['message']}")
                        st.error(f"Missing fields: {result.get('missing_fields', [])}")
                    else:
                        st.error(f"❌ {result['message']}")
    
    # Move buttons outside the form
    if st.session_state.get('jd_generated', False) and st.session_state.get('jd_content'):
        st.markdown("### 📋 Job Description Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Save button
            if st.button("💾 Save Job Description", type="primary"):
                try:
                    # Get the current form data from session state
                    current_form_data = st.session_state.get('jd_metadata', {})
                    
                    # Save using root agent
                    save_result = root_agent.generate_job_description(current_form_data)
                    if save_result['success']:
                        st.success("✅ Job description saved successfully!")
                    else:
                        st.error(f"❌ Error saving job description: {save_result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Error saving job description: {str(e)}")
        
        with col2:
            # Option to generate new JD
            if st.button("🔄 Generate New Job Description"):
                st.session_state.jd_generated = False
                st.session_state.jd_content = ""
                st.session_state.jd_metadata = {}
                st.session_state.parsed_job_details = {}  # Clear parsed details too
                st.rerun()

def generate_job_description_ui(root_agent):
    """Generate job description UI"""
    st.markdown("### 📝 Generate Job Description")
    
    with st.form("job_description_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input("Job Title*", placeholder="e.g., Senior Software Engineer")
            company_name = st.text_input("Company Name*", placeholder="e.g., Tech Corp")
            experience_required = st.text_input("Experience Required*", placeholder="e.g., 5+ years")
            employment_type = st.selectbox("Employment Type*", ["Full-time", "Part-time", "Contract", "Internship"])
        
        with col2:
            salary_range = st.text_input("Salary Range*", placeholder="e.g., $80,000 - $100,000")
            industry = st.text_input("Industry", value="Technology", placeholder="e.g., Technology")
            location = st.text_input("Location", value="Remote", placeholder="e.g., Remote")
            department = st.text_input("Department", value="Engineering", placeholder="e.g., Engineering")
        
        submitted = st.form_submit_button("🚀 Generate Job Description", type="primary")
        
        if submitted:
            if job_title and company_name and experience_required and salary_range:
                job_details = {
                    'job_title': job_title,
                    'company_name': company_name,
                    'experience_required': experience_required,
                    'employment_type': employment_type,
                    'salary_range': salary_range,
                    'industry': industry,
                    'location': location,
                    'department': department
                }
                
                with st.spinner("🤖 Generating job description..."):
                    result = root_agent.route_job_description_request(job_details)
                
                if result['success']:
                    st.success("✅ Job description generated successfully!")
                    
                    # Display the generated description
                    st.markdown("### 📄 Generated Job Description")
                    st.text_area("Job Description", result['description'], height=400, disabled=True)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Job Description",
                        data=result['description'],
                        file_name=f"{job_title.replace(' ', '_')}_job_description.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(f"❌ Error: {result['message']}")
            else:
                st.error("❌ Please fill in all required fields marked with *")

def analyze_resume_ui(root_agent):
    """Analyze resume UI"""
    st.markdown("### 📋 Resume Analysis")
    
    # Get available job descriptions
    job_descriptions = root_agent.get_available_job_descriptions()
    
    if not job_descriptions:
        st.warning("⚠️ No job descriptions available. Please generate a job description first.")
        return
    
    # Job description selection
    jd_options = [f"{jd['metadata']['job_title']} at {jd['metadata']['company_name']}" for jd in job_descriptions]
    selected_jd_index = st.selectbox("Select Job Description", range(len(jd_options)), format_func=lambda x: jd_options[x])
    
    selected_jd = job_descriptions[selected_jd_index]
    
    with st.form("resume_analysis_form"):
        candidate_name = st.text_input("Candidate Name*", placeholder="e.g., John Doe")
        candidate_email = st.text_input("Candidate Email", placeholder="e.g., john.doe@email.com")
        
        # Resume upload
        uploaded_file = st.file_uploader("Upload Resume*", type=['txt', 'pdf', 'docx'], help="Upload resume file")
        
        # Or paste content
        resume_content = st.text_area("Or Paste Resume Content", height=200, placeholder="Paste resume content here...")
        
        submitted = st.form_submit_button("🔍 Analyze Resume", type="primary")
        
        if submitted:
            if candidate_name and (uploaded_file or resume_content):
                # Process resume content
                if uploaded_file:
                    resume_text = extract_text_from_file(uploaded_file)
                else:
                    resume_text = resume_content
                
                resume_data = {
                    'content': resume_text,
                    'candidate_name': candidate_name,
                    'candidate_email': candidate_email,
                    'file_name': uploaded_file.name if uploaded_file else f"{candidate_name}_resume.txt"
                }
                
                job_description_data = {
                    'content': selected_jd['content'],
                    'job_title': selected_jd['metadata']['job_title'],
                    'company_name': selected_jd['metadata']['company_name']
                }
                
                with st.spinner("🤖 Analyzing resume..."):
                    result = root_agent.route_resume_analysis_request(resume_data, job_description_data)
                
                if result['success']:
                    st.success("✅ Resume analysis completed!")
                    
                    analysis = result['analysis_result']
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Overall Score", f"{analysis['overall_score']}/100")
                    
                    with col2:
                        skills_score = analysis['skills_analysis'].get('skill_score', 0)
                        st.metric("Skills Score", f"{skills_score}/100")
                    
                    with col3:
                        exp_score = analysis['experience_analysis'].get('experience_score', 0)
                        st.metric("Experience Score", f"{exp_score}/100")
                    
                    # Detailed analysis
                    with st.expander("📊 Detailed Analysis", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**💪 Strengths:**")
                            for strength in analysis['strengths'][:5]:
                                st.write(f"• {strength}")
                        
                        with col2:
                            st.markdown("**⚠️ Weaknesses:**")
                            for weakness in analysis['weaknesses'][:5]:
                                st.write(f"• {weakness}")
                    
                    # Recommendations
                    with st.expander("💡 Recommendations"):
                        for rec in analysis['recommendations'][:5]:
                            st.write(f"• {rec}")
                else:
                    st.error(f"❌ Error: {result['message']}")
            else:
                st.error("❌ Please provide candidate name and resume content")

def show_resume_analyzer(root_agent):
    """Resume Analyzer Page"""
    st.markdown('<h2 class="sub-header">📊 Resume Analyzer</h2>', unsafe_allow_html=True)
    
    # Get available job descriptions
    job_descriptions = root_agent.get_available_job_descriptions()
    
    if not job_descriptions:
        st.warning("⚠️ No saved job descriptions found!")
        st.info("Please create a job description first using the Job Description Generator.")
        if st.button("📝 Generate Job Description", type="primary"):
            st.session_state.current_page = "JD Generator"
            st.rerun()
        return
    
    # Job Description Selection
    st.markdown("### 📋 Select Job Description to Analyze Against")
    
    # Create a selection box for available JDs
    jd_options = [f"{jd['metadata']['job_title']} at {jd['metadata']['company_name']}" for jd in job_descriptions]
    selected_jd_index = st.selectbox(
        "Choose a job description:",
        range(len(job_descriptions)),
        format_func=lambda x: jd_options[x],
        help="Select a saved job description to analyze resumes against"
    )
    
    if selected_jd_index is not None:
        selected_jd = job_descriptions[selected_jd_index]
        
        # Display selected JD info
        st.success(f"✅ Selected: **{selected_jd['metadata']['job_title']}** at **{selected_jd['metadata']['company_name']}**")
        
        # Show JD preview
        with st.expander("📄 Preview Selected Job Description"):
            st.text_area("Job Description", selected_jd['content'], height=200, disabled=True)
        
        # Resume upload section
        st.markdown("### 📄 Upload Resume")
        st.markdown("""
        **Supported formats:** PDF, DOCX, TXT, JPG, JPEG
        
        **Instructions:**
        - Drag and drop your resume file below, or click to browse
        - The system will automatically extract text from your resume
        - For images: Ensure they are clear, well-lit, and contain readable text
        - Make sure your resume is clear and well-formatted for best analysis
        """)
        
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=['pdf', 'docx', 'txt', 'jpg', 'jpeg'],
            help="Upload your resume in PDF, DOCX, TXT, JPG, or JPEG format"
        )
        
        # Show file preview if uploaded
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Show image preview for image files
            file_extension = uploaded_file.name.lower().split('.')[-1]
            if file_extension in ['jpg', 'jpeg']:
                st.image(uploaded_file, caption="Uploaded Resume Image", use_container_width=True)
            
            # Extract text from file
            resume_content = extract_text_from_file(uploaded_file)
            
            if resume_content:
                # Show preview of extracted text
                with st.expander("📄 Preview Extracted Resume Content"):
                    st.text_area("Resume Content Preview", resume_content, height=200, disabled=True)
                
                # Extract and display candidate name
                extracted_name = extract_candidate_name(resume_content)
                st.info(f"📝 **Detected Candidate Name:** {extracted_name}")
                
                # Allow manual name correction
                candidate_name = st.text_input(
                    "Candidate Name (edit if needed):",
                    value=extracted_name,
                    help="The system detected this name from your resume. You can edit it if needed."
                )
                
                # Extract and display candidate email
                extracted_email = extract_candidate_email(resume_content)
                if extracted_email:
                    st.info(f"📧 **Detected Email:** {extracted_email}")
                    candidate_email = st.text_input(
                        "Candidate Email (edit if needed):",
                        value=extracted_email,
                        help="The system detected this email from your resume. You can edit it if needed."
                    )
                else:
                    st.warning("⚠️ **No email detected in resume**")
                    candidate_email = st.text_input(
                        "Enter Candidate Email:",
                        placeholder="candidate@email.com",
                        help="Please enter the candidate's email address"
                    )
                
                # Analysis button
                if st.button("🔍 Analyze Resume", type="primary"):
                    if len(resume_content.strip()) < 20:
                        st.error("❌ Resume content is too short. Please provide at least 20 characters of resume content.")
                    elif len(set(resume_content.lower().split())) < 3:
                        st.error("❌ Resume content lacks variety. Please provide more diverse information about your experience, skills, and qualifications.")
                    else:
                        # Check for placeholder text - only for very obvious cases
                        placeholder_indicators = ['test test test', 'sample sample sample', 'placeholder placeholder']
                        if any(indicator in resume_content.lower() for indicator in placeholder_indicators):
                            st.error("❌ Resume appears to contain obvious placeholder text. Please provide actual resume content.")
                        else:
                            analyze_resume_with_jd(root_agent, uploaded_file.name, resume_content, selected_jd, candidate_name, candidate_email)
            else:
                st.error("❌ Could not extract text from the uploaded file. Please try a different file.")
    
    # Option to create new JD
    st.markdown("---")
    st.markdown("### 🆕 Don't see the job description you need?")
    if st.button("📝 Create New Job Description"):
        st.session_state.current_page = "JD Generator"
        st.rerun()

def analyze_resume_with_jd(root_agent, file_name, resume_content, selected_jd, candidate_name, candidate_email):
    """Analyze resume against selected job description"""
    
    with st.spinner("🤖 Analyzing resume..."):
        try:
            # Prepare resume data
            resume_data = {
                'content': resume_content,
                'candidate_name': candidate_name,
                'candidate_email': candidate_email,
                'file_name': file_name
            }
            
            # Prepare job description data
            job_description_data = {
                'content': selected_jd['content'],
                'job_title': selected_jd['metadata']['job_title'],
                'company_name': selected_jd['metadata']['company_name']
            }
            
            # Analyze the resume using root agent
            result = root_agent.analyze_resume(resume_data, job_description_data)
            
            if result['success']:
                # Save to session state
                st.session_state.analysis_result = result['analysis_result']
                
                # Display results
                display_analysis_results(result['analysis_result'])
                
                # Show success message with candidate name
                st.success(f"✅ Resume analysis completed for **{candidate_name}**!")
                
            else:
                st.error(f"❌ Error analyzing resume: {result['error']}")
                
        except Exception as e:
            st.error(f"❌ Error analyzing resume: {str(e)}")

def display_analysis_results(analysis_result):
    """Display analysis results"""
    st.markdown("### 📊 Analysis Results")
    
    # Overall score
    overall_score = analysis_result['overall_score']
    score_class = get_score_color(overall_score)
    
    st.markdown(f"""
    <div class="score-display {score_class}">
        Overall Score: {overall_score}/100
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        skills_score = analysis_result['skills_analysis'].get('skill_match_percentage', 0)
        st.metric("Skills Match", f"{skills_score}%")
    
    with col2:
        experience_score = analysis_result['experience_analysis'].get('experience_score', 0)
        st.metric("Experience Score", f"{experience_score}/100")
    
    with col3:
        formatting_score = analysis_result['formatting_analysis'].get('overall_formatting_score', 0)
        st.metric("Formatting Score", f"{formatting_score}/100")
    
    # Strengths and Weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Strengths")
        for strength in analysis_result['strengths']:
            st.markdown(f"• {strength}")
    
    with col2:
        st.markdown("### ⚠️ Areas for Improvement")
        for weakness in analysis_result['weaknesses']:
            st.markdown(f"• {weakness}")
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    for i, rec in enumerate(analysis_result['recommendations'], 1):
        st.markdown(f"{i}. {rec}")
    
    # Detailed report
    with st.expander("📄 View Detailed Analysis Report"):
        st.markdown(analysis_result['final_report'])

def show_results():
    """Results page to view saved analyses"""
    st.markdown('<h2 class="sub-header">📋 Analysis Results</h2>', unsafe_allow_html=True)
    
    if st.session_state.analysis_result:
        display_analysis_results(st.session_state.analysis_result)
    else:
        st.info("No analysis results available. Please analyze a resume first.")

def show_system_status(root_agent):
    """System Status Page"""
    st.markdown('<h2 class="sub-header">🔧 System Status</h2>', unsafe_allow_html=True)
    
    # Get system status
    status = root_agent.get_system_status()
    
    # System overview
    st.markdown("### System Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("System Status", status['status'].title())
    
    with col2:
        job_descriptions = root_agent.get_available_job_descriptions()
        st.metric("Job Descriptions", len(job_descriptions))
    
    with col3:
        analysis_history = root_agent.get_analysis_history()
        st.metric("Analysis Results", len(analysis_history))
    
    # Agent status
    st.markdown("### Agent Status")
    for agent, state in status['agents'].items():
        st.markdown(f"**{agent.replace('_', ' ').title()}:** {state}")
    
    # Directory information
    st.markdown("### Directory Information")
    for name, path in status['directories'].items():
        st.markdown(f"**{name.replace('_', ' ').title()}:** {path}")
    
    # Configuration
    st.markdown("### Configuration")
    config = status['config']
    st.json(config)

def show_interview_scheduler(root_agent):
    """Interview Scheduler Page"""
    st.markdown('<h2 class="sub-header">📧 Interview Scheduler</h2>', unsafe_allow_html=True)
    
    # Debug section - add this temporarily
    with st.expander("🔍 Debug: Scheduler Agent Status"):
        try:
            if 'scheduler_agent' in st.session_state:
                scheduler = st.session_state.scheduler_agent
                st.write(f"**Scheduler Agent Type:** {type(scheduler).__name__}")
                st.write(f"**Scheduler Agent Class:** {scheduler.__class__.__name__}")
                st.write(f"**Has process_candidate method:** {hasattr(scheduler, 'process_candidate')}")
                if hasattr(scheduler, 'process_candidate'):
                    st.write(f"**Method signature:** {scheduler.process_candidate.__code__.co_varnames}")
            else:
                st.write("**Scheduler Agent:** Not initialized")
        except Exception as e:
            st.error(f"Debug error: {e}")
    
    # Description
    st.markdown("""
    This agent processes candidate analysis results and automatically sends appropriate emails based on their scores.
    - **Scores ≥ 50**: Automatically shortlisted with interview scheduling and Google Meet integration
    - **Scores < 50**: Rejection emails with constructive feedback
    - **Professional email templates** with company branding
    - **Calendar integration** for interview scheduling
    """)
    
    # Initialize scheduler agent
    if 'scheduler_agent' not in st.session_state:
        try:
            # Force fresh import to avoid caching issues
            import importlib
            import agents.interview_scheduler.interview_scheduler_agent as scheduler_module
            importlib.reload(scheduler_module)
            
            from agents.interview_scheduler.interview_scheduler_agent import InterviewSchedulerAgent
            st.session_state.scheduler_agent = InterviewSchedulerAgent()
            
        except Exception as e:
            st.error(f"Failed to initialize scheduler agent: {e}")
            return
    
    # Load candidates from analysis results
    if 'candidates' not in st.session_state:
        st.session_state.candidates = load_candidates_from_analysis(root_agent)
    
    # Add refresh button to reload candidates
    st.info("""
        **To get started:**
        1. Use the Resume Analyzer to analyze candidate resumes
        2. Return here to process the analysis results
        3. Send appropriate emails based on scores
        """)
    
    if st.button("🔄 Refresh Candidates", help="Reload candidates with latest data"):
        st.session_state.candidates = load_candidates_from_analysis(root_agent)
        st.rerun()
    
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
            
            # Main content area
            show_candidate_details_integrated(selected_candidate)
            show_action_buttons_integrated(selected_candidate)
            
            # Email preview section
            st.markdown("---")
            action = st.radio(
                "Preview Email Template:",
                ["Shortlisted Email", "Rejection Email"],
                horizontal=True
            )
            
            if action == "Shortlisted Email":
                show_email_preview_integrated(selected_candidate, 'shortlist')
            else:
                show_email_preview_integrated(selected_candidate, 'rejection')
    
    else:
        st.warning("⚠️ No candidates found!")
    
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

def load_candidates_from_analysis(root_agent):
    """Load candidates from analysis results"""
    try:
        from datetime import datetime
        
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
            
            # Get email from metadata, or try to extract from analysis data
            candidate_email = metadata.get('candidate_email', 'No email found')
            
            # If email is not found or is example.com, try to extract from resume content
            if candidate_email == 'No email found' or 'example.com' in candidate_email:
                # Try to find email in the analysis data or resume content
                candidate_email = extract_email_from_analysis_data(data)
            
            # Create candidate data
            candidate = {
                'name': candidate_name,
                'email': candidate_email,
                'score': overall_score,
                'job_title': 'Software Engineer',  # Placeholder - would come from analysis
                'company_name': 'Your Company',
                'resume_filename': f"{candidate_name}_resume.txt",
                'analysis_date': analysis_date,
                'status': 'pending',
                'analysis_data': data
            }
            
            # Only add candidates that have valid data
            if candidate['name'] and candidate['name'] != 'Unknown':
                candidates.append(candidate)
        
        return candidates
        
    except Exception as e:
        st.error(f"Error loading candidates: {e}")
        return []

def extract_email_from_analysis_data(analysis_data):
    """Extract email from analysis data if available"""
    try:
        # Check if there's any text content in the analysis that might contain email
        import re
        
        # Convert analysis data to string to search for email
        analysis_text = str(analysis_data)
        
        # Email regex pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, analysis_text)
        
        if emails:
            # Filter out example.com emails and return the first valid one
            for email in emails:
                email_lower = email.lower()
                if not any(skip in email_lower for skip in ['example.com', 'test.com', 'sample.com', 'placeholder']):
                    return email
            
            # If all emails were filtered out, return the first one anyway
            return emails[0] if emails else 'No email found'
        else:
            return 'No email found'
            
    except Exception as e:
        return 'No email found'

def show_candidate_details_integrated(candidate):
    """Display candidate details and analysis"""
    st.markdown("### 📋 Candidate Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Name", candidate['name'])
        
        # Handle email display with warning if not found
        if candidate['email'] == 'No email found':
            st.warning("⚠️ **Email not found in resume**")
            candidate['email'] = st.text_input(
                "📧 Enter Candidate Email:",
                placeholder="candidate@email.com",
                key=f"email_{candidate['name']}",
                help="Please enter the candidate's email address manually"
            )
        else:
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
    score_class = get_score_color(score)
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

def show_action_buttons_integrated(candidate):
    """Show action buttons based on candidate score"""
    st.markdown("### 🎯 Take Action")
    
    score = candidate['score']
    
    # Check if email is available
    email_available = candidate['email'] and candidate['email'] != 'No email found' and '@' in candidate['email']
    
    if not email_available:
        st.error("⚠️ **Email address required!** Please enter a valid email address for the candidate before taking action.")
        return
    
    if score >= 50:
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <h4 style="color: #28a745;">🎉 Candidate Qualifies for Interview!</h4>
            <p>This candidate has scored above the threshold and can be shortlisted for an interview.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ SHORTLIST CANDIDATE", type="primary", use_container_width=True, key=f"shortlist_{candidate['name']}"):
                process_shortlist_integrated(candidate)
        
        with col2:
            if st.button("❌ REJECT CANDIDATE", type="secondary", use_container_width=True, key=f"reject_{candidate['name']}"):
                process_rejection_integrated(candidate)
    
    else:
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <h4 style="color: #dc3545;">⚠️ Candidate Below Threshold</h4>
            <p>This candidate has scored below the minimum threshold for this position.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ OVERRIDE & SHORTLIST", type="secondary", use_container_width=True, key=f"override_{candidate['name']}"):
                process_shortlist_integrated(candidate)
        
        with col2:
            if st.button("❌ REJECT CANDIDATE", type="primary", use_container_width=True, key=f"reject_low_{candidate['name']}"):
                process_rejection_integrated(candidate)

def process_shortlist_integrated(candidate):
    """Process shortlist action"""
    try:
        scheduler = st.session_state.scheduler_agent
        if scheduler is None:
            st.error("Scheduler agent not available")
            return
        
        from agents.interview_scheduler.interview_scheduler_agent import CandidateData
        
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
            
            # Show interview details if available
            if 'interview_details' in result and result['interview_details']:
                st.markdown("### 📅 Interview Details")
                details = result['interview_details']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Date:** {details.get('interview_date', 'TBD')}")
                    st.info(f"**Time:** {details.get('interview_time', 'TBD')}")
                
                with col2:
                    st.info(f"**Meeting Link:** {details.get('meet_link', 'TBD')}")
                    st.info(f"**Confirmation:** {details.get('confirmation_link', 'TBD')}")
            
            # Update candidate status
            candidate['status'] = 'shortlisted'
            
        else:
            st.error(f"❌ {result['message']}")
    
    except Exception as e:
        st.error(f"❌ Error processing shortlist: {str(e)}")

def process_rejection_integrated(candidate):
    """Process rejection action"""
    try:
        scheduler = st.session_state.scheduler_agent
        if scheduler is None:
            st.error("Scheduler agent not available")
            return
        
        from agents.interview_scheduler.interview_scheduler_agent import CandidateData
        
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

def show_email_preview_integrated(candidate, action):
    """Show email preview"""
    st.markdown("### 📧 Email Preview")
    
    scheduler = st.session_state.scheduler_agent
    if scheduler is None:
        return
    
    if action == 'shortlist':
        template = scheduler.shortlisted_template
        
        # Create placeholder interview details for preview
        interview_details = scheduler._create_placeholder_interview(candidate['name'], candidate['job_title'])
        
        subject = template.subject.format(job_title=candidate['job_title'])
        body = template.body.format(
            candidate_name=candidate['name'],
            job_title=candidate['job_title'],
            company_name=candidate['company_name'],
            score=candidate['score'],
            interview_date=interview_details.interview_date,
            interview_time=interview_details.interview_time,
            meet_link=interview_details.meet_link,
            confirmation_link=interview_details.confirmation_link,
            duration=interview_details.duration,
            format=interview_details.format,
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

if __name__ == "__main__":
    main()
