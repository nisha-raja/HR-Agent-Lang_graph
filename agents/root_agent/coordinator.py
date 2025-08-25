"""
Root Agent Coordinator - Pure coordination between agents
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

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
