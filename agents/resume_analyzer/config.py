"""
Configuration Management for Resume Analyzer Agent
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ResumeAnalyzerConfig:
    """Configuration for Resume Analyzer Agent"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.analysis_results_dir = self.data_dir / "analysis_results"
        self.resumes_dir = self.data_dir / "resumes"
        
        # Ensure directories exist
        self.analysis_results_dir.mkdir(parents=True, exist_ok=True)
        self.resumes_dir.mkdir(parents=True, exist_ok=True)
        
        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
        
        # Analysis Configuration
        self.analysis_criteria = {
            'skills_weight': 0.3,
            'experience_weight': 0.4,
            'formatting_weight': 0.2,
            'overall_weight': 0.1
        }
        
        self.scoring_ranges = {
            'excellent': (85, 100),
            'good': (70, 84),
            'fair': (50, 69),
            'poor': (0, 49)
        }
        
        self.required_sections = [
            'contact_information',
            'summary_or_objective',
            'work_experience',
            'education',
            'skills'
        ]
        
        self.optional_sections = [
            'certifications',
            'projects',
            'volunteer_work',
            'languages',
            'interests'
        ]
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            'openai_model': self.openai_model,
            'openai_temperature': self.openai_temperature,
            'analysis_criteria': self.analysis_criteria,
            'scoring_ranges': self.scoring_ranges,
            'required_sections': self.required_sections,
            'optional_sections': self.optional_sections
        }
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        if not self.analysis_results_dir.exists():
            raise ValueError(f"Analysis results directory does not exist: {self.analysis_results_dir}")
        
        if not self.resumes_dir.exists():
            raise ValueError(f"Resumes directory does not exist: {self.resumes_dir}")
        
        return True
