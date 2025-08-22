"""
Job Description Generator Agent using LangGraph
A sophisticated workflow-based agent for creating professional job descriptions
"""

import os
import json
from typing import Dict, Any, List, TypedDict, Annotated
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import json
from dotenv import load_dotenv

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

class LangGraphJDGenerator:
    """LangGraph-based Job Description Generator Agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
    def get_job_details_from_user(self) -> JobDetails:
        """Get job details from user input"""
        print("📝 LangGraph JD Generator Agent")
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
        """Generate job overview section"""
        
        prompt = f"""
        Create a compelling job overview for a {state['job_details'].job_title} position at {state['job_details'].company_name}.
        
        Job Details:
        - Title: {state['job_details'].job_title}
        - Experience: {state['job_details'].experience_required}
        - Employment Type: {state['job_details'].employment_type}
        - Industry: {state['job_details'].industry}
        - Location: {state['job_details'].location}
        - Department: {state['job_details'].department}
        
        Write a 2-3 sentence job overview that:
        1. Introduces the role and its importance
        2. Mentions the company culture and values
        3. Highlights growth opportunities
        4. Uses inclusive and engaging language
        5. Avoids jargon and maintains a positive tone
        
        Focus on what makes this role exciting and what the company offers to candidates.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        state['job_overview'] = response.content
        state['current_step'] = "overview_complete"
        
        # Add to messages for context
        state['messages'].append({
            "role": "user",
            "content": f"Generated job overview for {state['job_details'].job_title}"
        })
        
        return state
    
    def create_responsibilities(self, state: JobDescriptionState) -> JobDescriptionState:
        """Generate responsibilities section"""
        
        prompt = f"""
        Create a focused list of key responsibilities for a {state['job_details'].job_title} position.
        
        Context:
        - Job Title: {state['job_details'].job_title}
        - Experience Level: {state['job_details'].experience_required}
        - Industry: {state['job_details'].industry}
        - Employment Type: {state['job_details'].employment_type}
        
        Generate 4-6 core responsibilities that:
        1. Are the most important and impactful for this role
        2. Align with the experience level
        3. Cover primary job functions
        4. Are clear and measurable
        5. Use action verbs at the beginning of each point
        6. Focus on essential duties, not every possible task
        
        Format as a numbered list with each responsibility on a new line.
        """
        
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
            "content": f"Generated {len(responsibilities)} responsibilities for {state['job_details'].job_title}"
        })
        
        return state
    
    def create_qualifications(self, state: JobDescriptionState) -> JobDescriptionState:
        """Generate qualifications section"""
        
        prompt = f"""
        Create a structured qualifications section for a {state['job_details'].job_title} position with three clear categories.
        
        Context:
        - Job Title: {state['job_details'].job_title}
        - Experience Level: {state['job_details'].experience_required}
        - Industry: {state['job_details'].industry}
        - Employment Type: {state['job_details'].employment_type}
        
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
        
        Format with clear category headers and bullet points under each.
        """
        
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
            "content": f"Generated {len(qualifications)} qualifications for {state['job_details'].job_title}"
        })
        
        return state
    
    def create_benefits(self, state: JobDescriptionState) -> JobDescriptionState:
        """Generate benefits section"""
        
        prompt = f"""
        Create a focused benefits section for a {state['job_details'].job_title} position at {state['job_details'].company_name}.
        
        Context:
        - Job Title: {state['job_details'].job_title}
        - Employment Type: {state['job_details'].employment_type}
        - Industry: {state['job_details'].industry}
        - Location: {state['job_details'].location}
        - Salary Range: {state['job_details'].salary_range}
        
        Generate a concise benefits package with the most attractive and relevant benefits:
        
        Core Benefits (4-6 key benefits):
        - Focus on the most important benefits for this role/industry
        - Include competitive compensation, health benefits, work-life balance
        - Highlight unique or standout benefits
        - Keep it realistic for the industry and company size
        
        Guidelines:
        1. Focus on quality over quantity
        2. Include benefits that matter most to candidates
        3. Use inclusive language
        4. Keep the tone positive and appealing
        5. Avoid listing every possible benefit - focus on the best ones
        
        Format as bullet points with clear, concise descriptions.
        """
        
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
            "content": f"Generated {len(benefits)} benefits for {state['job_details'].job_title}"
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
        
        Job Details:
        - Title: {state['job_details'].job_title}
        - Company: {state['job_details'].company_name}
        - Employment Type: {state['job_details'].employment_type}
        - Experience: {state['job_details'].experience_required}
        - Salary: {state['job_details'].salary_range}
        - Location: {state['job_details'].location}
        
        Create a final job description that:
        1. Has a clear, professional structure
        2. Includes all sections with proper formatting
        3. Maintains consistent tone and style
        4. Is easy to read and scan
        5. Includes a call-to-action for applications
        6. Uses appropriate headers and bullet points
        7. Ensures qualifications are organized into three clear categories:
           - EDUCATION & CERTIFICATIONS
           - TECHNICAL SKILLS  
           - SOFT SKILLS & COMPETENCIES
        
        Format the output with clear section headers and professional styling.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        state['final_description'] = response.content
        state['current_step'] = "complete"
        
        # Add to messages for context
        state['messages'].append({
            "role": "user",
            "content": f"Compiled final job description for {state['job_details'].job_title}"
        })
        
        return state
    
    def create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for job description generation"""
        
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
        """Generate a complete job description"""
        try:
            # Initialize state
            state = JobDescriptionState(
                job_details=job_details,
                job_overview="",
                responsibilities=[],
                qualifications=[],
                benefits=[],
                final_description="",
                current_step="start",
                messages=[]
            )
            
            # Execute the workflow
            final_state = self.workflow.invoke(state)
            
            return final_state['final_description']
            
        except Exception as e:
            print(f"Error generating job description: {e}")
            return f"Error: {str(e)}"
    
    def generate_job_description_with_save(self, job_details: Dict[str, Any], file_manager) -> Dict[str, Any]:
        """Generate job description and save it using file manager"""
        try:
            # Convert dict to JobDetails object
            job_details_obj = JobDetails(**job_details)
            
            # Generate job description
            description = self.generate_job_description(job_details_obj)
            
            # Save job description using file manager
            filename, metadata_filename = file_manager.save_job_description(job_details, description)
            
            return {
                'success': True,
                'description': description,
                'filename': filename,
                'metadata_filename': metadata_filename,
                'message': 'Job description generated successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to generate job description'
            }
    
    def save_job_description(self, job_details: JobDetails, description: str) -> str:
        """Save job description to file and create metadata for resume analysis"""
        
        # Create filename
        filename = f"{job_details.job_title.replace(' ', '_')}_{job_details.company_name.replace(' ', '_')}_job_description.txt"
        
        # Save job description
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(description)
        
        # Create metadata for resume analysis
        metadata = {
            "job_title": job_details.job_title,
            "company_name": job_details.company_name,
            "experience_required": job_details.experience_required,
            "employment_type": job_details.employment_type,
            "salary_range": job_details.salary_range,
            "industry": job_details.industry,
            "location": job_details.location,
            "department": job_details.department,
            "description_file": filename,
            "description_content": description,
            "created_at": "2024-01-01"  # You can add datetime here
        }
        
        # Save metadata
        metadata_filename = f"{job_details.job_title.replace(' ', '_')}_{job_details.company_name.replace(' ', '_')}_metadata.json"
        with open(metadata_filename, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return filename, metadata_filename

    def parse_job_details_from_natural_language(self, text: str) -> Dict[str, Any]:
        """
        Parse job details from natural language text using LLM - Fully dynamic approach
        This method analyzes the text and extracts ALL relevant information dynamically
        """
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
            
            IMPORTANT: Only include fields that have actual information from the text. If a field is not mentioned, either omit it or set it to empty string.
            """
            
            # Use the LLM to parse the text
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse the JSON response
            try:
                parsed = json.loads(response.content)
                
                # Clean up the parsed data - ensure empty strings instead of None
                for key, value in parsed.items():
                    if value is None:
                        parsed[key] = ""
                        
                return parsed
                
            except json.JSONDecodeError:
                # Fallback to basic extraction if LLM response is not valid JSON
                return self._fallback_parse_job_details(text)
                
        except Exception as e:
            print(f"❌ Error parsing with LLM: {str(e)}")
            # Fallback to basic extraction
            return self._fallback_parse_job_details(text)

    def _fallback_parse_job_details(self, text: str) -> Dict[str, Any]:
        """Fallback parsing method if LLM fails"""
        # Basic extraction for fallback
        parsed = {
            'job_title': 'Professional',
            'experience_required': '',
            'salary_range': '',
            'employment_type': '',
            'location': '',
            'industry': '',
            'department': '',
            'company_name': 'Your Company'
        }
        
        # Try to extract basic information using simple patterns
        text_lower = text.lower()
        
        # Extract job title (look for capitalized words)
        words = text.split()
        for word in words:
            if word[0].isupper() and len(word) > 3:
                parsed['job_title'] = word.title()
                break
        
        # Extract experience
        import re
        exp_match = re.search(r'(\d+)\s*(?:year|yr)s?\s*experience', text_lower)
        if exp_match:
            parsed['experience_required'] = f"{exp_match.group(1)}+ years"
        
        # Extract salary
        salary_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*(?:salary|range|aed|usd|eur)', text_lower)
        if salary_match:
            salary = salary_match.group(1)
            parsed['salary_range'] = f"{salary} - {int(salary) * 1.2}"
        
        return parsed

    def validate_job_details_form(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate job details form data
        Returns validation result with success status and any missing fields
        """
        required_fields = ['job_title', 'company_name', 'experience_required', 'employment_type', 'salary_range']
        missing_fields = []
        
        # Check each required field
        for field in required_fields:
            value = form_data.get(field, '').strip()
            if not value or value == '':
                missing_fields.append(field)
        
        # Return validation result
        return {
            'success': len(missing_fields) == 0,
            'missing_fields': missing_fields,
            'validated_data': form_data if len(missing_fields) == 0 else None,
            'message': f"Missing required fields: {', '.join(missing_fields)}" if missing_fields else "All required fields are valid"
        }
    
    def generate_dynamic_form_fields(self, parsed_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate dynamic form fields based on LLM parsed details
        Returns form configuration for UI rendering
        """
        # Standard form fields configuration
        standard_fields = {
            'job_title': {
                'type': 'text',
                'label': 'Job Title *',
                'placeholder': 'e.g., Senior Software Engineer',
                'required': True,
                'value': parsed_details.get('job_title', '')
            },
            'company_name': {
                'type': 'text',
                'label': 'Company Name *',
                'placeholder': 'e.g., TechCorp Inc.',
                'required': True,
                'value': parsed_details.get('company_name', '')
            },
            'experience_required': {
                'type': 'text',
                'label': 'Experience Required *',
                'placeholder': 'e.g., 5+ years',
                'required': True,
                'value': parsed_details.get('experience_required', '')
            },
            'employment_type': {
                'type': 'select',
                'label': 'Employment Type *',
                'options': ['Full-time', 'Part-time', 'Contract', 'Internship'],
                'required': True,
                'value': parsed_details.get('employment_type', 'Full-time')
            },
            'salary_range': {
                'type': 'text',
                'label': 'Salary Range *',
                'placeholder': 'e.g., $80,000 - $100,000',
                'required': True,
                'value': parsed_details.get('salary_range', '')
            },
            'industry': {
                'type': 'text',
                'label': 'Industry',
                'placeholder': 'e.g., Technology',
                'required': False,
                'value': parsed_details.get('industry', '')
            },
            'location': {
                'type': 'text',
                'label': 'Location',
                'placeholder': 'e.g., Remote',
                'required': False,
                'value': parsed_details.get('location', '')
            },
            'department': {
                'type': 'text',
                'label': 'Department',
                'placeholder': 'e.g., Engineering',
                'required': False,
                'value': parsed_details.get('department', '')
            }
        }
        
        # Dynamic fields based on LLM response
        dynamic_fields = {}
        for key, value in parsed_details.items():
            if key not in standard_fields and value:
                field_label = key.replace('_', ' ').title()
                
                if isinstance(value, str):
                    if value.lower() in ['yes', 'no', 'not specified']:
                        # Boolean/choice field
                        dynamic_fields[key] = {
                            'type': 'select',
                            'label': field_label,
                            'options': ['Not specified', 'Yes', 'No'],
                            'required': False,
                            'value': value
                        }
                    else:
                        # Text field
                        dynamic_fields[key] = {
                            'type': 'text',
                            'label': field_label,
                            'placeholder': f"Enter {field_label.lower()}",
                            'required': False,
                            'value': value
                        }
        
        return {
            'standard_fields': standard_fields,
            'dynamic_fields': dynamic_fields,
            'form_config': {
                'columns': 2,
                'sections': [
                    {
                        'title': 'Job Details',
                        'icon': '📋',
                        'fields': ['job_title', 'company_name', 'experience_required', 'employment_type', 'salary_range', 'industry', 'location', 'department']
                    },
                    {
                        'title': 'Additional Requirements',
                        'icon': '🔧',
                        'fields': list(dynamic_fields.keys())
                    }
                ]
            }
        }
    
    def process_form_submission(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process form submission and generate job description
        Returns result with success status and generated content
        """
        try:
            # Validate form data
            validation_result = self.validate_job_details_form(form_data)
            
            if not validation_result['success']:
                return {
                    'success': False,
                    'error': 'validation_failed',
                    'message': validation_result['message'],
                    'missing_fields': validation_result['missing_fields']
                }
            
            # Convert validated data to JobDetails object
            validated_data = validation_result['validated_data']
            job_details = JobDetails(**validated_data)
            
            # Generate job description using existing workflow
            description = self.generate_job_description(job_details)
            
            return {
                'success': True,
                'job_description': description,
                'job_details': validated_data,
                'message': 'Job description generated successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'generation_failed',
                'message': f'Error generating job description: {str(e)}'
            }
    
    def get_form_validation_rules(self) -> Dict[str, Any]:
        """
        Get form validation rules for UI implementation
        Returns validation configuration that can be used by any UI framework
        """
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

def main():
    """Main function to run the LangGraph JD Generator Agent"""
    
    try:
        # Initialize the agent
        generator = LangGraphJDGenerator()
        
        # Get job details from user
        job_details = generator.get_job_details_from_user()
        
        print("\n" + "=" * 50)
        print("🤖 LangGraph JD Generator Agent Processing...")
        print("=" * 50)
        
        # Generate the job description using LangGraph workflow
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
        
        print("\n🎉 LangGraph JD Generator Agent completed successfully!")
        
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