"""
HR Root Agent - Main Coordinator
Manages and coordinates all HR sub-agents including JD Generator and Resume Analyzer
"""

import os
import sys
import re # Added for parsing natural language text
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from agents.jd_generator.jd_generator_agent import LangGraphJDGenerator, JobDetails
from agents.resume_analyzer.resume_analyzer_agent import LangGraphResumeAnalyzer, ResumeData, JobDescriptionData
from agents.interview_scheduler.interview_scheduler_agent import InterviewSchedulerAgent, CandidateData
from utils.file_manager import FileManager
from utils.config_manager import ConfigManager

def parse_job_details_from_text(text):
    """Parse job details from natural language text"""
    import re
    text = text.lower().strip()
    parsed = {}
    
    # Job title patterns
    job_title_patterns = [
        r'(?:junior|senior|lead|principal|staff)\s+(?:developer|engineer|programmer|software\s+engineer)',
        r'(?:frontend|backend|full\s*stack|web|mobile|data|devops|qa|test)\s+(?:developer|engineer)',
        r'(?:ui|ux|product|project|business|data|system)\s+(?:designer|manager|analyst|architect)',
        r'(?:marketing|sales|hr|finance|legal|operations)\s+(?:manager|specialist|coordinator|assistant)'
    ]
    
    for pattern in job_title_patterns:
        match = re.search(pattern, text)
        if match:
            parsed['job_title'] = match.group().title()
            break
    
    if 'job_title' not in parsed:
        if 'developer' in text or 'engineer' in text:
            parsed['job_title'] = 'Software Developer'
        else:
            parsed['job_title'] = 'Professional'
    
    # Experience patterns
    exp_patterns = [
        r'(\d+)\s*(?:year|yr)s?\s*experience',
        r'experience\s*:\s*(\d+)\s*(?:year|yr)s?',
        r'(\d+)\s*(?:year|yr)s?\s*exp'
    ]
    
    for pattern in exp_patterns:
        match = re.search(pattern, text)
        if match:
            years = match.group(1)
            parsed['experience_required'] = f"{years}+ years"
            break
    
    if 'experience_required' not in parsed:
        parsed['experience_required'] = '1+ years'
    
    # Salary patterns
    salary_patterns = [
        r'(\d{1,3}(?:,\d{3})*)\s*(?:salary|range|aed|usd|eur)',
        r'salary\s*(?:range)?\s*:?\s*(\d{1,3}(?:,\d{3})*)',
        r'(\d{1,3}(?:,\d{3})*)\s*(?:to|-)\s*(\d{1,3}(?:,\d{3})*)'
    ]
    
    for pattern in salary_patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 2:
                parsed['salary_range'] = f"{match.group(1)} - {match.group(2)}"
            else:
                salary = match.group(1)
                parsed['salary_range'] = f"{salary} - {int(salary) * 1.2}"
            break
    
    if 'salary_range' not in parsed:
        parsed['salary_range'] = 'Competitive'
    
    # Employment type
    if 'full\s*time' in text or 'fulltime' in text:
        parsed['employment_type'] = 'Full-time'
    elif 'part\s*time' in text or 'parttime' in text:
        parsed['employment_type'] = 'Part-time'
    elif 'contract' in text:
        parsed['employment_type'] = 'Contract'
    elif 'intern' in text:
        parsed['employment_type'] = 'Internship'
    else:
        parsed['employment_type'] = 'Full-time'
    
    # Location
    location_patterns = [
        r'(?:in|at|location)\s*:?\s*([a-zA-Z\s]+)',
        r'(dubai|abudhabi|sharjah|ajman|ras\s*al\s*khaimah|fujairah|um\s*al\s*quwain)',
        r'(remote|onsite|hybrid)'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text)
        if match:
            parsed['location'] = match.group(1).strip().title()
            break
    
    if 'location' not in parsed:
        parsed['location'] = 'Dubai'
    
    # Industry
    industry_patterns = [
        r'(technology|tech|it|software|fintech|healthtech|edtech)',
        r'(banking|finance|insurance)',
        r'(healthcare|medical|pharmaceutical)',
        r'(education|e-learning|training)',
        r'(retail|e-commerce|fashion)',
        r'(manufacturing|automotive|aerospace)'
    ]
    
    for pattern in industry_patterns:
        match = re.search(pattern, text)
        if match:
            parsed['industry'] = match.group(1).title()
            break
    
    if 'industry' not in parsed:
        parsed['industry'] = 'Technology'
    
    # Skills extraction
    skill_patterns = [
        r'(python|java|javascript|js|react|angular|vue|node|php|ruby|go|rust|c\+\+|c#|swift|kotlin)',
        r'(html|css|sql|mongodb|postgresql|mysql|redis|docker|kubernetes|aws|azure|gcp)',
        r'(agile|scrum|kanban|waterfall|devops|ci/cd|git|jenkins|jira|confluence)'
    ]
    
    skills = []
    for pattern in skill_patterns:
        matches = re.findall(pattern, text)
        skills.extend(matches)
    
    if skills:
        parsed['skills'] = ', '.join(list(set(skills)))
    
    # Visa requirement
    if 'visa' in text and ('required' in text or 'need' in text or 'yes' in text):
        parsed['visa_required'] = 'Yes'
    elif 'visa' in text and ('not' in text or 'no' in text):
        parsed['visa_required'] = 'No'
    else:
        parsed['visa_required'] = 'Not specified'
    
    # Default values
    parsed['company_name'] = 'Your Company'
    
    # Department
    if 'frontend' in text or 'ui' in text or 'ux' in text:
        parsed['department'] = 'Frontend Development'
    elif 'backend' in text or 'api' in text or 'server' in text:
        parsed['department'] = 'Backend Development'
    elif 'full\s*stack' in text or 'fullstack' in text:
        parsed['department'] = 'Full Stack Development'
    elif 'data' in text or 'analytics' in text or 'ml' in text or 'ai' in text:
        parsed['department'] = 'Data Science'
    elif 'devops' in text or 'infrastructure' in text:
        parsed['department'] = 'DevOps'
    elif 'qa' in text or 'test' in text or 'quality' in text:
        parsed['department'] = 'Quality Assurance'
    else:
        parsed['department'] = 'Engineering'
    
    return parsed

class HRRootAgent:
    """Main HR Agent that coordinates all sub-agents"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.file_manager = FileManager()
        self.jd_generator = LangGraphJDGenerator()
        self.resume_analyzer = LangGraphResumeAnalyzer()
        self.interview_scheduler = InterviewSchedulerAgent()
        
        # Initialize data directories
        self.file_manager.ensure_directories()
    
    def generate_job_description(self, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a job description using the JD Generator agent"""
        try:
            # Convert dict to JobDetails object
            job_details_obj = JobDetails(**job_details)
            
            # Generate job description
            description = self.jd_generator.generate_job_description(job_details_obj)
            
            # Save job description using file manager
            filename, metadata_filename = self.file_manager.save_job_description(job_details, description)
            
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
    
    def analyze_resume(self, resume_data: Dict[str, Any], job_description_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a resume using the Resume Analyzer agent"""
        try:
            # Convert dicts to objects
            resume_obj = ResumeData(**resume_data)
            jd_obj = JobDescriptionData(**job_description_data)
            
            # Save resume file first
            resume_filename = self.file_manager.save_resume(resume_data, resume_data.get('file_name', 'resume.txt'))
            
            # Analyze resume
            analysis_result = self.resume_analyzer.analyze_resume(resume_obj, jd_obj)
            
            # Save analysis result
            candidate_email = getattr(resume_obj, 'candidate_email', None)
            analysis_filename = self.file_manager.save_analysis_result(analysis_result, resume_obj.candidate_name, candidate_email)
            
            return {
                'success': True,
                'analysis_result': analysis_result,
                'analysis_filename': analysis_filename,
                'resume_filename': resume_filename,
                'message': 'Resume analysis completed successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to analyze resume'
            }
    
    def get_available_job_descriptions(self) -> List[Dict[str, Any]]:
        """Get list of available job descriptions"""
        try:
            jd_files = self.file_manager.list_job_descriptions()
            job_descriptions = []
            
            for jd_file in jd_files:
                jd_content, jd_metadata = self.file_manager.load_job_description(jd_file)
                if jd_content and jd_metadata:
                    job_descriptions.append({
                        'filename': jd_file,
                        'content': jd_content,
                        'metadata': jd_metadata
                    })
            
            return job_descriptions
            
        except Exception as e:
            return []
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get list of previous analysis results"""
        try:
            analysis_files = self.file_manager.list_analysis_results()
            analysis_history = []
            
            for analysis_file in analysis_files:
                analysis_data = self.file_manager.load_analysis_result(analysis_file)
                if analysis_data:
                    analysis_history.append({
                        'filename': analysis_file,
                        'data': analysis_data
                    })
            
            return analysis_history
            
        except Exception as e:
            return []
    
    def delete_job_description(self, filename: str) -> Dict[str, Any]:
        """Delete a job description file"""
        try:
            success = self.file_manager.delete_job_description(filename)
            return {
                'success': success,
                'message': 'Job description deleted successfully' if success else 'Failed to delete job description'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to delete job description'
            }
    
    def delete_analysis_result(self, filename: str) -> Dict[str, Any]:
        """Delete an analysis result file"""
        try:
            success = self.file_manager.delete_analysis_result(filename)
            return {
                'success': success,
                'message': 'Analysis result deleted successfully' if success else 'Failed to delete analysis result'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to delete analysis result'
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health check"""
        try:
            return {
                'status': 'healthy',
                'agents': {
                    'jd_generator': 'active',
                    'resume_analyzer': 'active',
                    'interview_scheduler': 'active',
                    'root_agent': 'active'
                },
                'directories': {
                    'job_descriptions': self.file_manager.job_descriptions_dir,
                    'resumes': self.file_manager.resumes_dir,
                    'analysis_results': self.file_manager.analysis_results_dir
                },
                'config': self.config.get_config()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def process_candidate_for_interview(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process candidate for interview scheduling"""
        try:
            # Convert dict to CandidateData object
            candidate_obj = CandidateData(**candidate_data)
            
            # Process candidate using interview scheduler
            result = self.interview_scheduler.process_candidate(candidate_obj)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process candidate for interview'
            }
    
    def get_candidate_status(self, score: int) -> str:
        """Get candidate status based on score"""
        return self.interview_scheduler.get_candidate_status(score)
    
    def get_score_color(self, score: int) -> str:
        """Get color class based on score"""
        return self.interview_scheduler.get_score_color(score)

def main():
    """Main function to run the HR Root Agent"""
    print("🤖 HR Root Agent - Main Coordinator")
    print("=" * 50)
    
    # Initialize root agent
    root_agent = HRRootAgent()
    
    # Get system status
    status = root_agent.get_system_status()
    print(f"System Status: {status['status']}")
    
    # Show available job descriptions
    job_descriptions = root_agent.get_available_job_descriptions()
    print(f"Available Job Descriptions: {len(job_descriptions)}")
    
    # Show analysis history
    analysis_history = root_agent.get_analysis_history()
    print(f"Analysis History: {len(analysis_history)} results")
    
    print("\n🎉 HR Root Agent is ready to coordinate sub-agents!")

if __name__ == "__main__":
    main()
