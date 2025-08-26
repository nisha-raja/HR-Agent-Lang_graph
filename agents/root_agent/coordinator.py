"""
Root Agent Coordinator - Pure coordination between agents
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import re

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from agents.jd_generator import JDGeneratorAgent
from agents.resume_analyzer import ResumeAnalyzerAgent
from agents.interview_scheduler import InterviewSchedulerAgent

class RootAgentCoordinator:
    """Pure Coordinator Agent - Routes requests to appropriate sub-agents"""
    
    def __init__(self):
        # Initialize sub-agents
        self.jd_generator = JDGeneratorAgent()
        self.resume_analyzer = ResumeAnalyzerAgent()
        self.interview_scheduler = InterviewSchedulerAgent()
    
    # ==================== COORDINATION METHODS ====================
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agents"""
        return ['jd_generator', 'resume_analyzer', 'interview_scheduler']
    
    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get status of a specific agent"""
        try:
            if agent_name == 'jd_generator':
                return self.jd_generator.get_agent_status()
            elif agent_name == 'resume_analyzer':
                return self.resume_analyzer.get_agent_status()
            elif agent_name == 'interview_scheduler':
                return self.interview_scheduler.get_agent_status()
            else:
                return {'status': 'unknown', 'error': f'Unknown agent: {agent_name}'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            jd_status = self.jd_generator.get_agent_status()
            resume_status = self.resume_analyzer.get_agent_status()
            scheduler_status = self.interview_scheduler.get_agent_status()
            
            return {
                'status': 'healthy',
                'agents': {
                    'jd_generator': jd_status['status'],
                    'resume_analyzer': resume_status['status'], 
                    'interview_scheduler': scheduler_status['status']
                },
                'available_agents': self.get_available_agents(),
                'message': 'All agents are operational',
                'details': {
                    'jd_generator': jd_status,
                    'resume_analyzer': resume_status,
                    'interview_scheduler': scheduler_status
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'System error occurred'
            }
    
    # ==================== JD GENERATOR ROUTING ====================
    
    def generate_job_description(self, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Route job description generation to JD Generator Agent"""
        return self.jd_generator.generate_job_description_from_dict(job_details)
    
    def save_job_description(self, job_details: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Route job description saving to JD Generator Agent"""
        return self.jd_generator.save_job_description(job_details, description)
    
    def get_available_job_descriptions(self) -> List[Dict[str, Any]]:
        """Route job descriptions retrieval to JD Generator Agent"""
        return self.jd_generator.get_available_job_descriptions()
    
    def delete_job_description(self, filename: str) -> Dict[str, Any]:
        """Route job description deletion to JD Generator Agent"""
        return self.jd_generator.delete_job_description(filename)
    
    # ==================== AI ASSISTANT PARSING ====================
    
    def parse_job_details_from_text(self, text: str) -> Dict[str, Any]:
        """Parse job details from natural language text using LLM for intelligent parsing"""
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage, SystemMessage
            
            # Check if OpenAI API key is available
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return {
                    "success": False,
                    "validation_issues": ["OpenAI API key is not configured"],
                    "suggestions": ["Please configure your OpenAI API key in the environment variables"],
                    "message": "System configuration error",
                    "parsed_data": {}
                }
            
            # Initialize LLM
            llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.1,  # Low temperature for consistent parsing
                api_key=api_key
            )
            
            # System prompt for intelligent parsing
            system_prompt = """You are an expert job description parser. Your task is to intelligently parse job requirements from user input and extract structured data.

IMPORTANT RULES:
1. CORRECT ALL TYPOS automatically (e.g., "compary" → "company", "experince" → "experience", "yr" → "year")
2. VALIDATE inputs - if something looks invalid (like "sdfasdfadadas" as company name), mark it as invalid
3. HANDLE AMBIGUITY - if multiple job titles or unclear information, ask for clarification
4. SUGGEST CORRECTIONS for invalid job titles (e.g., "demo" is not a valid job title)
5. EXTRACT the most likely intended information

Parse the following job requirements and return a JSON object with these fields:
{
    "job_title": "string (corrected job title, or null if invalid/ambiguous)",
    "experience_required": "string (e.g., '0-2 years', '3-5 years', '6-8 years', '8+ years')",
    "company_name": "string (corrected company name, or null if invalid)",
    "employment_type": "string (Full-time, Part-time, Contract, Internship)",
    "salary_range": "string (e.g., '$5000', '$50000-70000')",
    "location": "string (job location)",
    "work_location_type": "string (Remote, On-site, Hybrid)",
    "visa_required": "boolean",
    "skills_required": "string (comma-separated skills)",
    "validation_issues": ["array of validation issues or clarification needed"],
    "suggestions": ["array of suggestions for corrections"]
}

EXAMPLES:
- "plumber, 5000 salary, 7+ year experince, rrr compary" → Correct typos and extract properly
- "demo, 5000 salary" → Mark job_title as invalid, suggest valid job titles
- "plumber, doctor, 5000 salary" → Mark as ambiguous, ask for clarification
- "sdfasdfadadas company" → Mark company_name as invalid

Return ONLY the JSON object, no additional text."""

            # Create the prompt
            prompt = f"Parse this job requirement text: {text}"
            
            # Get LLM response
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ])
            
            # Parse the JSON response
            import json
            try:
                # Clean the response content to extract JSON
                content = response.content.strip()
                
                # Try to find JSON in the response (in case LLM added extra text)
                if content.startswith('{') and content.endswith('}'):
                    json_str = content
                else:
                    # Try to extract JSON from the response
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = content[start_idx:end_idx]
                    else:
                        raise json.JSONDecodeError("No JSON found in response", content, 0)
                
                parsed_data = json.loads(json_str)
                
                # Check for validation issues
                validation_issues = parsed_data.get('validation_issues', [])
                suggestions = parsed_data.get('suggestions', [])
                
                # If there are validation issues, return them for user clarification
                if validation_issues:
                    return {
                        "success": False,
                        "validation_issues": validation_issues,
                        "suggestions": suggestions,
                        "message": "Please clarify the following issues before proceeding:",
                        "parsed_data": {k: v for k, v in parsed_data.items() if k not in ['validation_issues', 'suggestions']}
                    }
                
                # Remove validation fields from final result
                parsed_data.pop('validation_issues', None)
                parsed_data.pop('suggestions', None)
                
                # Set defaults for missing fields
                defaults = {
                    "employment_type": "Full-time",
                    "location": "Remote",
                    "work_location_type": "Remote",
                    "visa_required": False,
                    "skills_required": ""
                }
                
                for key, default_value in defaults.items():
                    if key not in parsed_data or parsed_data[key] is None:
                        parsed_data[key] = default_value
                
                return {
                    "success": True,
                    "parsed_data": parsed_data,
                    "message": "Job details parsed successfully"
                }
                
            except json.JSONDecodeError as e:
                # Provide more specific error message
                return {
                    "success": False,
                    "validation_issues": ["Unable to parse the job requirements properly"],
                    "suggestions": [
                        "Please provide job requirements in a clearer format",
                        "Example: 'software developer, 5000 salary, 3 years experience, tech company'"
                    ],
                    "message": "Please provide clearer job requirements",
                    "parsed_data": {},
                    "debug_info": f"JSON parsing error: {str(e)}"
                }
                
        except Exception as e:
            # Provide user-friendly error message
            error_msg = str(e)
            if "api_key" in error_msg.lower():
                return {
                    "success": False,
                    "validation_issues": ["OpenAI API configuration error"],
                    "suggestions": ["Please check your OpenAI API key configuration"],
                    "message": "System configuration error",
                    "parsed_data": {}
                }
            elif "rate limit" in error_msg.lower():
                return {
                    "success": False,
                    "validation_issues": ["Service temporarily unavailable"],
                    "suggestions": ["Please try again in a few moments"],
                    "message": "Service temporarily unavailable",
                    "parsed_data": {}
                }
            else:
                # Fallback: try to extract basic information even if LLM fails
                fallback_data = self._fallback_parse(text)
                if fallback_data:
                    return {
                        "success": True,
                        "parsed_data": fallback_data,
                        "message": "Job details parsed with basic extraction (some details may need manual review)"
                    }
                else:
                    return {
                        "success": False,
                        "validation_issues": ["Unable to process your request"],
                        "suggestions": [
                            "Please try again",
                            "Make sure your input is clear and complete",
                            "Example format: 'software developer, 5000 salary, 3 years experience, tech company'"
                        ],
                        "message": "Unable to process your request. Please try again.",
                        "parsed_data": {}
                    }
    
    def _fallback_parse(self, text: str) -> Dict[str, Any]:
        """Fallback parsing method when LLM fails"""
        try:
            text_lower = text.lower()
            parsed_data = {
                "job_title": "",
                "experience_required": "",
                "company_name": "",
                "employment_type": "Full-time",
                "salary_range": "",
                "location": "Remote",
                "work_location_type": "Remote",
                "visa_required": False,
                "skills_required": ""
            }
            
            # Basic extraction patterns
            import re
            
            # Extract salary
            salary_match = re.search(r'(\d+(?:,\d+)*)\s*(?:salary|aed|usd)', text_lower)
            if salary_match:
                salary = salary_match.group(1).replace(',', '')
                parsed_data["salary_range"] = f"${salary}"
            
            # Extract experience
            exp_match = re.search(r'(\d+)\s*(?:year|yr)s?\s*experience', text_lower)
            if exp_match:
                years = int(exp_match.group(1))
                if years <= 2:
                    parsed_data["experience_required"] = "0-2 years"
                elif years <= 5:
                    parsed_data["experience_required"] = "3-5 years"
                elif years <= 8:
                    parsed_data["experience_required"] = "6-8 years"
                else:
                    parsed_data["experience_required"] = "8+ years"
            
            # Extract job title (first word before comma)
            words = text.split(',')[0].strip().split()
            if words:
                parsed_data["job_title"] = words[0].title()
            
            # Extract company name
            company_match = re.search(r'(\w+)\s+company', text_lower)
            if company_match:
                parsed_data["company_name"] = company_match.group(1).title() + " Company"
            
            # Check for visa requirement
            if 'visa' in text_lower:
                parsed_data["visa_required"] = True
            
            # Check for remote work
            if 'remote' in text_lower:
                parsed_data["work_location_type"] = "Remote"
            
            return parsed_data
            
        except Exception:
            return {}
    
    # ==================== RESUME ANALYZER ROUTING ====================
    
    def analyze_resume(self, resume_data: Dict[str, Any], job_description_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route resume analysis to Resume Analyzer Agent"""
        try:
            # Use the new modular agent
            result = self.resume_analyzer.analyze_resume_from_dict(resume_data, job_description_data)
            
            # Convert response to dictionary format
            if hasattr(result, 'model_dump'):
                return result.model_dump()
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': 'analysis_failed',
                'message': f'Error analyzing resume: {str(e)}'
            }
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Route analysis history retrieval to Resume Analyzer Agent"""
        try:
            return self.resume_analyzer.get_analysis_history()
        except Exception as e:
            return []
    
    # ==================== INTERVIEW SCHEDULER ROUTING ====================
    
    def schedule_interview(self, candidate_data: Dict[str, Any], interview_details: Dict[str, Any]) -> Dict[str, Any]:
        """Route interview scheduling to Interview Scheduler Agent"""
        try:
            # Use the new modular agent
            result = self.interview_scheduler.schedule_interview_from_dict(candidate_data, interview_details)
            
            # Convert response to dictionary format
            if hasattr(result, 'model_dump'):
                return result.model_dump()
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': 'scheduling_failed',
                'message': f'Error scheduling interview: {str(e)}'
            }
    
    def process_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route candidate processing to Interview Scheduler Agent"""
        try:
            from agents.interview_scheduler.models import CandidateData as CandidateDataModel
            
            # Create CandidateData object
            candidate_obj = CandidateDataModel(
                name=candidate_data['name'],
                email=candidate_data['email'],
                score=candidate_data['score'],
                job_title=candidate_data['job_title'],
                company_name=candidate_data['company_name'],
                resume_filename=candidate_data.get('resume_filename', ''),
                analysis_date=candidate_data.get('analysis_date', '')
            )
            
            return self.interview_scheduler.process_candidate(candidate_obj)
            
        except Exception as e:
            return {
                'success': False,
                'error': 'processing_failed',
                'message': f'Error processing candidate: {str(e)}'
            }
    
    def get_email_templates(self) -> List[Dict[str, Any]]:
        """Route email templates retrieval to Interview Scheduler Agent"""
        try:
            return self.interview_scheduler.get_email_templates()
        except Exception as e:
            return []
    
    def suggest_interview_slots(self, date: str, duration: int = None) -> List[Dict[str, str]]:
        """Route interview slots suggestion to Interview Scheduler Agent"""
        try:
            return self.interview_scheduler.suggest_interview_slots(date, duration)
        except Exception as e:
            return []
    
    # ==================== BACKWARD COMPATIBILITY ====================
    
    def route_job_description_request(self, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Backward compatibility method"""
        return self.generate_job_description(job_details)
    
    def route_resume_analysis_request(self, resume_data: Dict[str, Any], job_description_data: Dict[str, Any]) -> Dict[str, Any]:
        """Backward compatibility method"""
        return self.analyze_resume(resume_data, job_description_data)
    
    def route_interview_scheduling_request(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Backward compatibility method"""
        # For backward compatibility, we need interview_details
        # This method signature might need to be updated in the UI
        return {
            'success': False,
            'error': 'missing_interview_details',
            'message': 'Interview details are required for scheduling. Use schedule_interview() method instead.'
        }
