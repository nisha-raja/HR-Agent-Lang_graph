"""
HR Root Agent - Pure Coordinator
Routes user requests to appropriate sub-agents based on requirements
"""

import os
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from agents.jd_generator.jd_generator_agent import SimpleRAGJDGenerator
from agents.resume_analyzer.resume_analyzer_agent import LangGraphResumeAnalyzer
from agents.interview_scheduler.interview_scheduler_agent import InterviewSchedulerAgent
from utils.file_manager import FileManager
from utils.config_manager import ConfigManager

class HRRootAgent:
    """Pure Coordinator Agent - Routes requests to appropriate sub-agents"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.file_manager = FileManager()
        
        # Initialize sub-agents
        self.jd_generator = SimpleRAGJDGenerator()
        self.resume_analyzer = LangGraphResumeAnalyzer()
        self.interview_scheduler = InterviewSchedulerAgent()
        
        # Initialize data directories
        self.file_manager.ensure_directories()
    
    # ==================== COORDINATION METHODS ====================
    
    def generate_job_description(self, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate job description using the RAG-enhanced JD Generator Agent"""
        return self.jd_generator.generate_job_description_from_dict(job_details)
    
    def route_job_description_request(self, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Route job description generation to JD Generator Agent (backward compatibility)"""
        return self.generate_job_description(job_details)
    
    def route_resume_analysis_request(self, resume_data: Dict[str, Any], job_description_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route resume analysis to Resume Analyzer Agent"""
        return self.resume_analyzer.analyze_resume_with_save(resume_data, job_description_data, self.file_manager)
    
    def route_interview_scheduling_request(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route interview scheduling to Interview Scheduler Agent"""
        return self.interview_scheduler.process_candidate_with_data(candidate_data)
    
    # ==================== SYSTEM STATUS & UTILITIES ====================
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health check"""
        try:
            # Get RAG stats from JD generator
            rag_stats = self.jd_generator.get_rag_stats()
            
            return {
                'status': 'healthy',
                'agents': {
                    'jd_generator': 'active',
                    'resume_analyzer': 'active',
                    'interview_scheduler': 'active',
                    'root_agent': 'active'
                },
                'rag_system': rag_stats,
                'directories': {
                    'job_descriptions': str(self.file_manager.job_descriptions_dir),
                    'resumes': str(self.file_manager.resumes_dir),
                    'analysis_results': str(self.file_manager.analysis_results_dir)
                },
                'config': self.config.get_config()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information"""
        return self.file_manager.get_storage_info()
    
    def get_available_job_descriptions(self) -> List[Dict[str, Any]]:
        """Get list of available job descriptions"""
        return self.file_manager.get_all_job_descriptions()
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get list of previous analysis results"""
        return self.file_manager.get_all_analysis_results()
    
    def delete_job_description(self, filename: str) -> Dict[str, Any]:
        """Delete a job description file"""
        return self.file_manager.delete_job_description_with_response(filename)
    
    def delete_analysis_result(self, filename: str) -> Dict[str, Any]:
        """Delete an analysis result file"""
        return self.file_manager.delete_analysis_result_with_response(filename)

def main():
    """Main function to run the HR Root Agent"""
    print("🤖 HR Root Agent - Pure Coordinator")
    print("=" * 50)
    
    # Initialize root agent
    root_agent = HRRootAgent()
    
    # Get system status
    status = root_agent.get_system_status()
    print(f"System Status: {status['status']}")
    
    # Show RAG system status
    if 'rag_system' in status:
        rag_stats = status['rag_system']
        print(f"RAG System: {rag_stats['status']}")
        if rag_stats['status'] == 'active':
            print(f" Documents in cache: {rag_stats['documents']}")
            print(f" Method: {rag_stats['method']}")
    
    # Show available job descriptions
    job_descriptions = root_agent.get_available_job_descriptions()
    print(f"Available Job Descriptions: {len(job_descriptions)}")
    
    # Show analysis history
    analysis_history = root_agent.get_analysis_history()
    print(f"Analysis History: {len(analysis_history)} results")
    
    print("\n🎉 HR Root Agent is ready to coordinate sub-agents!")

if __name__ == "__main__":
    main()
