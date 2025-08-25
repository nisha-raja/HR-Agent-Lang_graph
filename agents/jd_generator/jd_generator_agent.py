"""
Job Description Generator Agent using LangGraph with Simple RAG
A sophisticated workflow-based agent for creating professional job descriptions
with simple retrieval-augmented generation capabilities (Windows Compatible)
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, List, TypedDict, Annotated
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import json
from dotenv import load_dotenv
from pathlib import Path
from difflib import SequenceMatcher

# Load environment variables
load_dotenv()

class JobDetails(BaseModel):
    """Model for job details input"""
    job_title: str = Field(description="The title of the position")
    experience_required: str = Field(description="Required experience level")
    company_name: str = Field(description="Name of the hiring company")
    employment_type: str = Field(description="Full-time, Part-time, Contract, etc.")
    salary_range: str = Field(description="Salary range according to market standards")
    industry: str = Field(description="Industry or sector", default="Technology")
    location: str = Field(description="Job location", default="Remote")
    department: str = Field(description="Department or team", default="General")

class JobDescriptionState(TypedDict):
    """State for the job description generation workflow"""
    job_details: JobDetails
    job_overview: str
    responsibilities: List[str]
    qualifications: List[str]
    benefits: List[str]
    final_description: str
    current_step: str
    messages: List[Dict[str, Any]]
    retrieved_context: List[str]  # New field for RAG context

class SimpleRAGJDGenerator:
    """LangGraph-based Job Description Generator Agent with Simple RAG capabilities"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.job_descriptions_cache = []
        self.initialize_rag_system()
        
    def initialize_rag_system(self):
        """Initialize the simple RAG system with existing job descriptions"""
        try:
            print("🔧 Initializing simple RAG system...")
            self.load_existing_job_descriptions()
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize RAG system: {e}")
            print("Continuing without RAG capabilities...")
    
    def load_existing_job_descriptions(self):
        """Load existing job descriptions into memory"""
        try:
            job_descriptions_dir = Path("data/job_descriptions")
            
            if job_descriptions_dir.exists():
                print(f"📄 Scanning directory: {job_descriptions_dir}")
                for file_path in job_descriptions_dir.glob("*.txt"):
                    if "job_description" in file_path.name:
                        print(f"📄 Loading: {file_path.name}")
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Store job description with metadata
                        self.job_descriptions_cache.append({
                            "content": content,
                            "filename": file_path.name,
                            "file_path": str(file_path)
                        })
                
                print(f"✅ Loaded {len(self.job_descriptions_cache)} job descriptions into memory")
            else:
                print("ℹ️ No existing job descriptions found")
                print("💡 The system will work without RAG until you generate some job descriptions")
                
        except Exception as e:
            print(f"❌ Error loading job descriptions: {e}")
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using SequenceMatcher"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def retrieve_relevant_context(self, job_details: JobDetails, top_k: int = 3) -> List[str]:
        """Retrieve relevant job descriptions as context using simple text similarity"""
        if not self.job_descriptions_cache:
            return []
        
        try:
            # Create search query based on job details
            search_query = f"{job_details.job_title} {job_details.industry} {job_details.department} {job_details.experience_required}"
            
            print(f"🔍 Searching for relevant context: {search_query}")
            
            # Calculate similarity scores
            similarities = []
            for job_desc in self.job_descriptions_cache:
                similarity = self.calculate_similarity(search_query, job_desc["content"])
                similarities.append((similarity, job_desc))
            
            # Sort by similarity and get top k
            similarities.sort(key=lambda x: x[0], reverse=True)
            top_matches = similarities[:top_k]
            
            # Extract relevant content
            context = []
            for i, (similarity, job_desc) in enumerate(top_matches, 1):
                if similarity > 0.1:  # Only include if similarity is above threshold
                    # Extract key sections from the job description
                    sections = self.extract_relevant_sections(job_desc["content"])
                    if sections:
                        context.append(f"Reference Job Description {i} (Similarity: {similarity:.2f}):\n{sections}")
            
            if context:
                print(f"✅ Found {len(context)} relevant job descriptions for context")
            else:
                print("ℹ️ No relevant job descriptions found for this role")
            
            return context
            
        except Exception as e:
            print(f"⚠️ Warning: Error retrieving context: {e}")
            return []
    
    def extract_relevant_sections(self, content: str) -> str:
        """Extract relevant sections from job description content"""
        lines = content.split('\n')
        relevant_sections = []
        current_section = ""
        in_relevant_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header
            if any(keyword in line.lower() for keyword in ['overview', 'responsibilities', 'qualifications', 'requirements', 'skills']):
                in_relevant_section = True
                current_section = line
                relevant_sections.append(f"\n{line}")
            elif in_relevant_section and line:
                relevant_sections.append(line)
            elif line and not line.startswith('•') and not line.startswith('-') and not line.startswith('*'):
                # If we hit a new section that's not relevant, stop
                if any(keyword in line.lower() for keyword in ['benefits', 'compensation', 'application', 'contact']):
                    in_relevant_section = False
        
        return '\n'.join(relevant_sections)
    
    def get_job_details_from_user(self) -> JobDetails:
        """Get job details from user input"""
        print("📝 Simple RAG-Enhanced LangGraph JD Generator Agent")
        print("=" * 50)
        print("Enter the job details below:")
        print()
        
        job_title = input("Job Title: ").strip()
        company_name = input("Company Name: ").strip()
        experience_required = input("Experience Required (e.g., 5+ years): ").strip()
        employment_type = input("Employment Type (Full-time/Part-time/Contract): ").strip()
        salary_range = input("Salary Range (e.g., $80,000 - $100,000): ").strip()
        
        industry = input("Industry (press Enter for Technology): ").strip()
        industry = industry if industry else "Technology"
        
        location = input("Location (press Enter for Remote): ").strip()
        location = location if location else "Remote"
        
        department = input("Department (press Enter for General): ").strip()
        department = department if department else "General"
        
        return JobDetails(
            job_title=job_title,
            experience_required=experience_required,
            company_name=company_name,
            employment_type=employment_type,
            salary_range=salary_range,
            industry=industry,
            location=location,
            department=department
        )
    
    def create_job_overview(self, state: JobDescriptionState) -> JobDescriptionState:
        """Generate job overview section with RAG context"""
        
        # Get RAG context
        rag_context = ""
        if state.get('retrieved_context'):
            rag_context = "\n\nReference Job Descriptions:\n" + "\n---\n".join(state['retrieved_context'])
        
        prompt = f"""
        Create a compelling job overview for a {state['job_details'].job_title} position at {state['job_details'].company_name}.
        
        Job Details:
        - Title: {state['job_details'].job_title}
        - Experience: {state['job_details'].experience_required}
        - Employment Type: {state['job_details'].employment_type}
        - Industry: {state['job_details'].industry}
        - Location: {state['job_details'].location}
        - Department: {state['job_details'].department}
        
        {rag_context}
        
        Write a 2-3 sentence job overview that:
        1. Introduces the role and its importance
        2. Mentions the company culture and values
        3. Highlights growth opportunities
        4. Uses inclusive and engaging language
        5. Avoids jargon and maintains a positive tone
        6. Incorporates best practices from similar roles (if reference examples provided)
        
        Focus on what makes this role exciting and what the company offers to candidates.
        """
        
        print("📝 Generating job overview...")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        state['job_overview'] = response.content
        state['current_step'] = "overview_complete"
        
        # Add to messages for context
        state['messages'].append({
            "role": "user",
            "content": f"Generated job overview for {state['job_details'].job_title} with RAG context"
        })
        
        return state
    
    def create_responsibilities(self, state: JobDescriptionState) -> JobDescriptionState:
        """Generate responsibilities section with RAG context"""
        
        # Get RAG context
        rag_context = ""
        if state.get('retrieved_context'):
            rag_context = "\n\nReference Responsibilities:\n" + "\n---\n".join(state['retrieved_context'])
        
        prompt = f"""
        Create a focused list of key responsibilities for a {state['job_details'].job_title} position.
        
        Context:
        - Job Title: {state['job_details'].job_title}
        - Experience Level: {state['job_details'].experience_required}
        - Industry: {state['job_details'].industry}
        - Employment Type: {state['job_details'].employment_type}
        
        {rag_context}
        
        Generate 4-6 core responsibilities that:
        1. Are the most important and impactful for this role
        2. Align with the experience level
        3. Cover primary job functions
        4. Are clear and measurable
        5. Use action verbs at the beginning of each point
        6. Focus on essential duties, not every possible task
        7. Incorporate industry best practices from similar roles (if reference examples provided)
        
        Format as a numbered list with each responsibility on a new line.
        """
        
        print("📋 Generating responsibilities...")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        responsibilities_text = response.content
        
        # Parse the numbered list into individual items
        responsibilities = []
        for line in responsibilities_text.strip().split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-') or line.startswith('*')):
                # Remove numbering and formatting
                clean_line = line.lstrip('0123456789.•-* ').strip()
                if clean_line:
                    responsibilities.append(clean_line)
        
        state['responsibilities'] = responsibilities
        state['current_step'] = "responsibilities_complete"
        
        # Add to messages for context
        state['messages'].append({
            "role": "user", 
            "content": f"Generated {len(responsibilities)} responsibilities for {state['job_details'].job_title} with RAG context"
        })
        
        return state
    
    def create_qualifications(self, state: JobDescriptionState) -> JobDescriptionState:
        """Generate qualifications section with RAG context"""
        
        # Get RAG context
        rag_context = ""
        if state.get('retrieved_context'):
            rag_context = "\n\nReference Qualifications:\n" + "\n---\n".join(state['retrieved_context'])
        
        prompt = f"""
        Create a structured qualifications section for a {state['job_details'].job_title} position with three clear categories.
        
        Context:
        - Job Title: {state['job_details'].job_title}
        - Experience Level: {state['job_details'].experience_required}
        - Industry: {state['job_details'].industry}
        - Employment Type: {state['job_details'].employment_type}
        
        {rag_context}
        
        Organize qualifications into THREE categories:
        
        1. EDUCATION & CERTIFICATIONS:
        - Required education level
        - Relevant certifications
        - Academic background
        
        2. TECHNICAL SKILLS:
        - Required technical competencies
        - Tools and technologies
        - Industry-specific skills
        
        3. SOFT SKILLS & COMPETENCIES:
        - Communication skills
        - Leadership abilities
        - Problem-solving skills
        - Team collaboration
        
        Guidelines:
        1. Be realistic and inclusive
        2. Focus on essential requirements
        3. Keep each category concise (2-4 points each)
        4. Avoid unnecessary requirements that could exclude qualified candidates
        5. Use clear, specific language
        6. Incorporate industry standards from similar roles (if reference examples provided)
        
        Format with clear category headers and bullet points under each.
        """
        
        print("🎓 Generating qualifications...")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        qualifications_text = response.content
        
        # Parse qualifications into a list
        qualifications = []
        for line in qualifications_text.strip().split('\n'):
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                clean_line = line.lstrip('•-* ').strip()
                if clean_line:
                    qualifications.append(clean_line)
        
        state['qualifications'] = qualifications
        state['current_step'] = "qualifications_complete"
        
        # Add to messages for context
        state['messages'].append({
            "role": "user",
            "content": f"Generated {len(qualifications)} qualifications for {state['job_details'].job_title} with RAG context"
        })
        
        return state
    
    def create_benefits(self, state: JobDescriptionState) -> JobDescriptionState:
        """Generate benefits section with RAG context"""
        
        # Get RAG context
        rag_context = ""
        if state.get('retrieved_context'):
            rag_context = "\n\nReference Benefits:\n" + "\n---\n".join(state['retrieved_context'])
        
        prompt = f"""
        Create a focused benefits section for a {state['job_details'].job_title} position at {state['job_details'].company_name}.
        
        Context:
        - Job Title: {state['job_details'].job_title}
        - Employment Type: {state['job_details'].employment_type}
        - Industry: {state['job_details'].industry}
        - Location: {state['job_details'].location}
        - Salary Range: {state['job_details'].salary_range}
        
        {rag_context}
        
        Generate a concise benefits package with the most attractive and relevant benefits:
        
        Core Benefits (4-6 key benefits):
        - Focus on the most important benefits for this role/industry
        - Include competitive compensation, health benefits, work-life balance
        - Highlight unique or standout benefits
        - Keep it realistic for the industry and company size
        - Consider industry standards from similar roles (if reference examples provided)
        
        Guidelines:
        1. Focus on quality over quantity
        2. Include benefits that matter most to candidates
        3. Use inclusive language
        4. Keep the tone positive and appealing
        5. Avoid listing every possible benefit - focus on the best ones
        
        Format as bullet points with clear, concise descriptions.
        """
        
        print("💰 Generating benefits...")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        benefits_text = response.content
        
        # Parse benefits into a list
        benefits = []
        for line in benefits_text.strip().split('\n'):
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                clean_line = line.lstrip('•-* ').strip()
                if clean_line:
                    benefits.append(clean_line)
        
        state['benefits'] = benefits
        state['current_step'] = "benefits_complete"
        
        # Add to messages for context
        state['messages'].append({
            "role": "user",
            "content": f"Generated {len(benefits)} benefits for {state['job_details'].job_title} with RAG context"
        })
        
        return state
    
    def compile_final_description(self, state: JobDescriptionState) -> JobDescriptionState:
        """Compile all sections into a final, formatted job description"""
        
        prompt = f"""
        Compile a professional, well-formatted job description using the following sections:
        
        Job Overview:
        {state['job_overview']}
        
        Responsibilities:
        {chr(10).join([f"• {resp}" for resp in state['responsibilities']])}
        
        Qualifications:
        {chr(10).join([f"• {qual}" for qual in state['qualifications']])}
        
        Benefits:
        {chr(10).join([f"• {benefit}" for benefit in state['benefits']])}
        
        Create a final, polished job description that:
        1. Maintains consistent formatting and tone
        2. Flows naturally between sections
        3. Uses professional language
        4. Is easy to read and scan
        5. Includes all necessary information
        6. Ends with a compelling call to action
        
        Format the output as a complete job description with clear section headers.
        """
        
        print("📄 Compiling final job description...")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        state['final_description'] = response.content
        state['current_step'] = "complete"
        
        # Add to messages for context
        state['messages'].append({
            "role": "user",
            "content": "Compiled final job description"
        })
        
        return state
    
    def create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for job description generation"""
        
        # Create the state graph
        workflow = StateGraph(JobDescriptionState)
        
        # Add nodes
        workflow.add_node("create_overview", self.create_job_overview)
        workflow.add_node("create_responsibilities", self.create_responsibilities)
        workflow.add_node("create_qualifications", self.create_qualifications)
        workflow.add_node("create_benefits", self.create_benefits)
        workflow.add_node("compile_final", self.compile_final_description)
        
        # Define the workflow
        workflow.set_entry_point("create_overview")
        workflow.add_edge("create_overview", "create_responsibilities")
        workflow.add_edge("create_responsibilities", "create_qualifications")
        workflow.add_edge("create_qualifications", "create_benefits")
        workflow.add_edge("create_benefits", "compile_final")
        workflow.add_edge("compile_final", END)
        
        return workflow.compile()
    
    def generate_job_description(self, job_details: JobDetails) -> str:
        """Generate a complete job description using the LangGraph workflow"""
        
        # Retrieve relevant context using RAG
        retrieved_context = self.retrieve_relevant_context(job_details)
        
        # Initialize state
        initial_state = JobDescriptionState(
            job_details=job_details,
            job_overview="",
            responsibilities=[],
            qualifications=[],
            benefits=[],
            final_description="",
            current_step="start",
            messages=[],
            retrieved_context=retrieved_context
        )
        
        # Create and run the workflow
        workflow = self.create_workflow()
        result = workflow.invoke(initial_state)
        
        return result['final_description']
    
    def save_job_description(self, job_details: JobDetails, description: str) -> tuple[str, str]:
        """Save the generated job description and metadata"""
        
        # Create filename
        safe_title = "".join(c for c in job_details.job_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"data/job_descriptions/{safe_title}_{timestamp}_job_description.txt"
        metadata_filename = f"data/job_descriptions/{safe_title}_{timestamp}_metadata.json"
        
        # Ensure directory exists
        os.makedirs("data/job_descriptions", exist_ok=True)
        
        # Save job description
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(description)
        
        # Save metadata
        metadata = {
            "job_title": job_details.job_title,
            "company_name": job_details.company_name,
            "experience_required": job_details.experience_required,
            "employment_type": job_details.employment_type,
            "salary_range": job_details.salary_range,
            "industry": job_details.industry,
            "location": job_details.location,
            "department": job_details.department,
            "generated_at": datetime.now().isoformat(),
            "agent_version": "Simple RAG-Enhanced v1.0 (Windows Compatible)",
            "rag_context_used": True if self.job_descriptions_cache else False
        }
        
        with open(metadata_filename, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Add new job description to cache for future RAG
        self.job_descriptions_cache.append({
            "content": description,
            "filename": filename,
            "file_path": filename
        })
        
        print("✅ Added new job description to RAG cache")
        
        return filename, metadata_filename
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system"""
        try:
            stats = {
                "status": "active" if self.job_descriptions_cache else "no_data",
                "documents": len(self.job_descriptions_cache),
                "method": "Simple Text Similarity"
            }
            
            return stats
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Add these methods INSIDE the SimpleRAGJDGenerator class, right after the get_rag_stats method

    def process_form_submission(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process form submission from UI and generate job description (without auto-saving)"""
        
        try:
            # Validate form data
            if not form_data.get('job_title') or not form_data.get('company_name'):
                return {
                    'success': False,
                    'error': 'missing_required_fields',
                    'message': 'Job title and company name are required'
                }
            
            # Create JobDetails object from form data
            job_details = JobDetails(
                job_title=form_data.get('job_title', ''),
                company_name=form_data.get('company_name', ''),
                experience_required=form_data.get('experience_required', ''),
                employment_type=form_data.get('employment_type', 'Full-time'),
                salary_range=form_data.get('salary_range', ''),
                industry=form_data.get('industry', 'Technology'),
                location=form_data.get('location', 'Remote'),
                department=form_data.get('department', 'General')
            )
            
            # Generate job description using RAG (without auto-saving)
            print("🤖 Generating job description with RAG...")
            description = self.generate_job_description(job_details)
            
            # Return the generated description without saving (user will save manually)
            return {
                'success': True,
                'job_description': description,
                'job_details': {
                    'job_title': job_details.job_title,
                    'company_name': job_details.company_name,
                    'experience_required': job_details.experience_required,
                    'employment_type': job_details.employment_type,
                    'salary_range': job_details.salary_range,
                    'industry': job_details.industry,
                    'location': job_details.location,
                    'department': job_details.department
                },
                'message': 'Job description generated successfully. Click "Save Job Description" to save it.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'generation_failed',
                'message': f'Error generating job description: {str(e)}'
            }

    def get_form_validation_rules(self) -> Dict[str, Any]:
        """Get form validation rules for UI implementation"""
        return {
            'required_fields': ['job_title', 'company_name', 'experience_required', 'employment_type', 'salary_range'],
            'field_types': {
                'job_title': 'text',
                'company_name': 'text',
                'experience_required': 'text',
                'employment_type': 'select',
                'salary_range': 'text',
                'industry': 'text',
                'location': 'text',
                'department': 'text'
            },
            'validation_patterns': {
                'job_title': r'^[a-zA-Z\s\-\.]+$',
                'company_name': r'^[a-zA-Z\s\-\.&]+$',
                'experience_required': r'^[\d\s\-\+]+(?:years?|yrs?)?$',
                'salary_range': r'^[\$\d,\s\-]+$'
            },
            'error_messages': {
                'job_title': 'Job title is required and should contain only letters, spaces, hyphens, and periods',
                'company_name': 'Company name is required and should contain only letters, spaces, hyphens, periods, and ampersands',
                'experience_required': 'Experience is required and should be in format like "5+ years" or "3-5 years"',
                'employment_type': 'Employment type is required',
                'salary_range': 'Salary range is required and should be in format like "$80,000 - $100,000"'
            }
        }

    def validate_job_details(self, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Validate job details and return validation result"""
        
        required_fields = ['job_title', 'company_name', 'experience_required', 'employment_type', 'salary_range']
        missing_fields = []
        
        for field in required_fields:
            if not job_details.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            return {
                'valid': False,
                'missing_fields': missing_fields,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }
        
        return {
            'valid': True,
            'message': 'All required fields are present'
        }

    def generate_job_description_from_dict(self, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate job description from dictionary input (for backward compatibility)"""
        
        try:
            # Validate input
            validation = self.validate_job_details(job_details)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'validation_failed',
                    'message': validation['message'],
                    'missing_fields': validation.get('missing_fields', [])
                }
            
            # Create JobDetails object
            job_details_obj = JobDetails(
                job_title=job_details.get('job_title', ''),
                company_name=job_details.get('company_name', ''),
                experience_required=job_details.get('experience_required', ''),
                employment_type=job_details.get('employment_type', 'Full-time'),
                salary_range=job_details.get('salary_range', ''),
                industry=job_details.get('industry', 'Technology'),
                location=job_details.get('location', 'Remote'),
                department=job_details.get('department', 'General')
            )
            
            # Generate job description using RAG
            print("🤖 Generating job description with RAG...")
            description = self.generate_job_description(job_details_obj)
            
            # Save the job description
            filename, metadata_filename = self.save_job_description(job_details_obj, description)
            
            return {
                'success': True,
                'job_description': description,
                'job_details': job_details,
                'filename': filename,
                'metadata_filename': metadata_filename,
                'message': 'Job description generated successfully with RAG'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'generation_failed',
                'message': f'Error generating job description: {str(e)}'
            }

# Keep the original class for backward compatibility
LangGraphJDGenerator = SimpleRAGJDGenerator
RAGEnhancedJDGenerator = SimpleRAGJDGenerator

def main():
    """Main function to run the Simple RAG-Enhanced LangGraph JD Generator Agent"""
    
    try:
        # Initialize the agent
        generator = SimpleRAGJDGenerator()
        
        # Show RAG stats
        rag_stats = generator.get_rag_stats()
        print(f" RAG System Status: {rag_stats['status']}")
        if rag_stats['status'] == 'active':
            print(f"📚 Documents in cache: {rag_stats['documents']}")
            print(f"📚 Method: {rag_stats['method']}")
        
        # Get job details from user
        job_details = generator.get_job_details_from_user()
        
        print("\n" + "=" * 50)
        print("🤖 Simple RAG-Enhanced LangGraph JD Generator Agent Processing...")
        print("=" * 50)
        
        # Generate the job description using LangGraph workflow with RAG
        description = generator.generate_job_description(job_details)
        
        print("\n" + "=" * 50)
        print("📄 Generated Job Description")
        print("=" * 50)
        print(description)
        
        # Save job description and metadata
        filename, metadata_filename = generator.save_job_description(job_details, description)
        
        print(f"\n✅ Job description saved to: {filename}")
        print(f"✅ Metadata saved to: {metadata_filename}")
        
        # Ask if user wants to analyze a resume against this job description
        analyze_resume = input("\n🔍 Would you like to analyze a resume against this job description? (y/n): ").strip().lower()
        
        if analyze_resume == 'y':
            print(f"\n🚀 To analyze a resume, run:")
            print(f"python resume_analyzer_agent.py")
            print(f"\n📋 Use these details:")
            print(f"• Job Title: {job_details.job_title}")
            print(f"• Company Name: {job_details.company_name}")
            print(f"• Job Description: Copy from the file '{filename}'")
        
        print("\n🎉 Simple RAG-Enhanced LangGraph JD Generator Agent completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. OpenAI API key in .env file")
        print("2. Internet connection")
        print("3. Valid API key with credits")
        print("4. LangGraph dependencies installed")

if __name__ == "__main__":
    main() 