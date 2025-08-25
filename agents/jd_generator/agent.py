"""
Pure JD Generator Agent - Self-contained job description generation
"""

import os
import json
from typing import Dict, Any, List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .models import JobDetails, JobDescriptionResponse, ValidationResult, RAGStats
from .config import JDGeneratorConfig
from .utils import JDFileManager, JDValidator, RAGUtils

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
    retrieved_context: List[str]

class JDGeneratorAgent:
    """Pure JD Generator Agent - Self-contained and deployable independently"""
    
    def __init__(self):
        # Initialize configuration
        self.config = JDGeneratorConfig()
        self.config.validate_config()
        
        # Initialize utilities
        self.file_manager = JDFileManager(self.config.job_descriptions_dir)
        self.validator = JDValidator(self.config.get_config())
        self.rag_utils = RAGUtils()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.config.openai_model,
            temperature=self.config.openai_temperature,
            api_key=self.config.openai_api_key
        )
        
        # Initialize RAG cache
        self.job_descriptions_cache = []
        self._load_job_descriptions_cache()
    
    def _load_job_descriptions_cache(self):
        """Load job descriptions into RAG cache"""
        try:
            self.job_descriptions_cache = self.file_manager.load_job_descriptions()
            print(f"✅ Loaded {len(self.job_descriptions_cache)} job descriptions into RAG cache")
        except Exception as e:
            print(f"⚠️ Warning: Error loading job descriptions cache: {e}")
            self.job_descriptions_cache = []
    
    def retrieve_relevant_context(self, job_details: JobDetails, top_k: int = 3) -> List[str]:
        """Retrieve relevant job descriptions as context using simple text similarity"""
        if not self.job_descriptions_cache:
            return []
        
        try:
            # Create search query based on job details
            search_query = f"{job_details.job_title} {job_details.industry} {job_details.department} {job_details.experience_required}"
            
            # Calculate similarity scores
            similarities = []
            for job_desc in self.job_descriptions_cache:
                similarity = self.rag_utils.calculate_similarity(search_query, job_desc["content"])
                similarities.append((similarity, job_desc))
            
            # Sort by similarity and get top k
            similarities.sort(key=lambda x: x[0], reverse=True)
            top_matches = similarities[:top_k]
            
            # Extract relevant content
            context = []
            for i, (similarity, job_desc) in enumerate(top_matches, 1):
                if similarity > self.config.rag_similarity_threshold:
                    sections = self.rag_utils.extract_relevant_sections(job_desc["content"])
                    if sections:
                        context.append(f"Reference Job Description {i} (Similarity: {similarity:.2f}):\n{sections}")
            
            return context
            
        except Exception as e:
            print(f"⚠️ Warning: Error retrieving context: {e}")
            return []
    
    def create_job_overview(self, state: JobDescriptionState) -> JobDescriptionState:
        """Generate job overview section with RAG context"""
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
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        state['job_overview'] = response.content
        state['current_step'] = "overview_complete"
        
        state['messages'].append({
            "role": "user",
            "content": f"Generated job overview for {state['job_details'].job_title} with RAG context"
        })
        
        return state
    
    def create_responsibilities(self, state: JobDescriptionState) -> JobDescriptionState:
        """Generate responsibilities section with RAG context"""
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
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        responsibilities_text = response.content
        
        # Parse the numbered list into individual items
        responsibilities = []
        for line in responsibilities_text.strip().split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-') or line.startswith('*')):
                clean_line = line.lstrip('0123456789.•-* ').strip()
                if clean_line:
                    responsibilities.append(clean_line)
        
        state['responsibilities'] = responsibilities
        state['current_step'] = "responsibilities_complete"
        
        state['messages'].append({
            "role": "user",
            "content": f"Generated {len(responsibilities)} responsibilities for {state['job_details'].job_title}"
        })
        
        return state
    
    def create_qualifications(self, state: JobDescriptionState) -> JobDescriptionState:
        """Generate qualifications section with RAG context"""
        rag_context = ""
        if state.get('retrieved_context'):
            rag_context = "\n\nReference Qualifications:\n" + "\n---\n".join(state['retrieved_context'])
        
        prompt = f"""
        Create a comprehensive list of qualifications for a {state['job_details'].job_title} position.
        
        Context:
        - Job Title: {state['job_details'].job_title}
        - Experience Level: {state['job_details'].experience_required}
        - Industry: {state['job_details'].industry}
        - Employment Type: {state['job_details'].employment_type}
        
        {rag_context}
        
        Generate 4-6 qualifications that include:
        1. Required education level
        2. Required experience
        3. Required skills and certifications
        4. Preferred qualifications
        5. Industry-specific requirements
        6. Incorporate best practices from similar roles (if reference examples provided)
        
        Format as a numbered list with each qualification on a new line.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        qualifications_text = response.content
        
        # Parse the numbered list into individual items
        qualifications = []
        for line in qualifications_text.strip().split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-') or line.startswith('*')):
                clean_line = line.lstrip('0123456789.•-* ').strip()
                if clean_line:
                    qualifications.append(clean_line)
        
        state['qualifications'] = qualifications
        state['current_step'] = "qualifications_complete"
        
        state['messages'].append({
            "role": "user",
            "content": f"Generated {len(qualifications)} qualifications for {state['job_details'].job_title}"
        })
        
        return state
    
    def create_benefits(self, state: JobDescriptionState) -> JobDescriptionState:
        """Generate benefits section"""
        prompt = f"""
        Create an attractive benefits section for a {state['job_details'].job_title} position at {state['job_details'].company_name}.
        
        Context:
        - Job Title: {state['job_details'].job_title}
        - Industry: {state['job_details'].industry}
        - Employment Type: {state['job_details'].employment_type}
        - Salary Range: {state['job_details'].salary_range}
        
        Generate 4-6 benefits that:
        1. Are competitive for the industry and role
        2. Include standard benefits (health, dental, vision)
        3. Include modern perks (flexible work, professional development)
        4. Are attractive to candidates
        5. Align with the employment type
        6. Use engaging and positive language
        
        Format as a numbered list with each benefit on a new line.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        benefits_text = response.content
        
        # Parse the numbered list into individual items
        benefits = []
        for line in benefits_text.strip().split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-') or line.startswith('*')):
                clean_line = line.lstrip('0123456789.•-* ').strip()
                if clean_line:
                    benefits.append(clean_line)
        
        state['benefits'] = benefits
        state['current_step'] = "benefits_complete"
        
        state['messages'].append({
            "role": "user",
            "content": f"Generated {len(benefits)} benefits for {state['job_details'].job_title}"
        })
        
        return state
    
    def create_final_description(self, state: JobDescriptionState) -> JobDescriptionState:
        """Create the final job description"""
        prompt = f"""
        Create a complete, professional job description for a {state['job_details'].job_title} position at {state['job_details'].company_name}.
        
        Job Details:
        - Title: {state['job_details'].job_title}
        - Company: {state['job_details'].company_name}
        - Experience: {state['job_details'].experience_required}
        - Employment Type: {state['job_details'].employment_type}
        - Salary Range: {state['job_details'].salary_range}
        - Industry: {state['job_details'].industry}
        - Location: {state['job_details'].location}
        - Department: {state['job_details'].department}
        
        Generated Content:
        - Overview: {state['job_overview']}
        - Responsibilities: {chr(10).join(f"• {resp}" for resp in state['responsibilities'])}
        - Qualifications: {chr(10).join(f"• {qual}" for qual in state['qualifications'])}
        - Benefits: {chr(10).join(f"• {benefit}" for benefit in state['benefits'])}
        
        Create a complete job description that:
        1. Starts with the job title and company name
        2. Includes the overview section
        3. Lists responsibilities clearly
        4. Lists qualifications clearly
        5. Includes benefits section
        6. Ends with application instructions
        7. Uses professional formatting
        8. Is engaging and attractive to candidates
        
        Format the job description professionally with clear sections and bullet points.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        state['final_description'] = response.content
        state['current_step'] = "complete"
        
        state['messages'].append({
            "role": "user",
            "content": f"Generated complete job description for {state['job_details'].job_title}"
        })
        
        return state
    
    def create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(JobDescriptionState)
        
        # Add nodes
        workflow.add_node("create_overview", self.create_job_overview)
        workflow.add_node("create_responsibilities", self.create_responsibilities)
        workflow.add_node("create_qualifications", self.create_qualifications)
        workflow.add_node("create_benefits", self.create_benefits)
        workflow.add_node("create_final_description", self.create_final_description)
        
        # Add edges
        workflow.set_entry_point("create_overview")
        workflow.add_edge("create_overview", "create_responsibilities")
        workflow.add_edge("create_responsibilities", "create_qualifications")
        workflow.add_edge("create_qualifications", "create_benefits")
        workflow.add_edge("create_benefits", "create_final_description")
        workflow.add_edge("create_final_description", END)
        
        return workflow.compile()
    
    def generate_job_description(self, job_details: JobDetails) -> str:
        """Generate a job description using the workflow"""
        # Retrieve relevant context for RAG
        retrieved_context = []
        if self.config.rag_enabled:
            retrieved_context = self.retrieve_relevant_context(job_details, self.config.rag_top_k)
        
        # Initialize state
        state = JobDescriptionState(
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
        
        # Execute workflow
        final_state = self.create_workflow().invoke(state)
        
        return final_state['final_description']
    
    def generate_job_description_from_dict(self, job_details: Dict[str, Any]) -> JobDescriptionResponse:
        """Generate job description from dictionary input"""
        try:
            # Validate input
            validation = self.validator.validate_job_details(job_details)
            if not validation['valid']:
                return JobDescriptionResponse(
                    success=False,
                    error='validation_failed',
                    message=validation['message']
                )
            
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
            
            # Generate job description
            description = self.generate_job_description(job_details_obj)
            
            return JobDescriptionResponse(
                success=True,
                job_description=description,
                job_details=job_details,
                message='Job description generated successfully'
            )
            
        except Exception as e:
            return JobDescriptionResponse(
                success=False,
                error='generation_failed',
                message=f'Error generating job description: {str(e)}'
            )
    
    def save_job_description(self, job_details: Dict[str, Any], description: str) -> JobDescriptionResponse:
        """Save a job description"""
        try:
            filename, metadata_filename = self.file_manager.save_job_description(job_details, description)
            
            # Reload cache to include new job description
            self._load_job_descriptions_cache()
            
            return JobDescriptionResponse(
                success=True,
                job_description=description,
                job_details=job_details,
                filename=filename,
                metadata_filename=metadata_filename,
                message='Job description saved successfully'
            )
            
        except Exception as e:
            return JobDescriptionResponse(
                success=False,
                error='save_failed',
                message=f'Error saving job description: {str(e)}'
            )
    
    def get_available_job_descriptions(self) -> List[Dict[str, Any]]:
        """Get all available job descriptions"""
        return self.file_manager.load_job_descriptions()
    
    def delete_job_description(self, filename: str) -> JobDescriptionResponse:
        """Delete a job description"""
        try:
            success = self.file_manager.delete_job_description(filename)
            if success:
                # Reload cache
                self._load_job_descriptions_cache()
                return JobDescriptionResponse(
                    success=True,
                    message=f'Job description {filename} deleted successfully'
                )
            else:
                return JobDescriptionResponse(
                    success=False,
                    error='delete_failed',
                    message=f'Failed to delete job description {filename}'
                )
        except Exception as e:
            return JobDescriptionResponse(
                success=False,
                error='delete_failed',
                message=f'Error deleting job description: {str(e)}'
            )
    
    def get_rag_stats(self) -> RAGStats:
        """Get RAG system statistics"""
        try:
            return RAGStats(
                status="active" if self.job_descriptions_cache else "no_data",
                documents=len(self.job_descriptions_cache),
                method="Simple Text Similarity"
            )
        except Exception as e:
            return RAGStats(
                status="error",
                documents=0,
                method="Simple Text Similarity",
                error=str(e)
            )
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'status': 'healthy',
            'config': self.config.get_config(),
            'rag_stats': self.get_rag_stats().dict(),
            'job_descriptions_count': len(self.job_descriptions_cache)
        }
