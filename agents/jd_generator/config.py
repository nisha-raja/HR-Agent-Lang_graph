"""
Configuration Management for JD Generator Agent
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class JDGeneratorConfig:
    """Configuration for JD Generator Agent"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.job_descriptions_dir = self.data_dir / "job_descriptions"
        
        # Ensure directories exist
        self.job_descriptions_dir.mkdir(parents=True, exist_ok=True)
        
        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        # RAG Configuration
        self.rag_enabled = os.getenv("RAG_ENABLED", "true").lower() == "true"
        self.rag_top_k = int(os.getenv("RAG_TOP_K", "3"))
        self.rag_similarity_threshold = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.1"))
        
        # Validation Configuration
        self.required_fields = [
            'job_title', 'company_name', 'experience_required', 
            'employment_type', 'salary_range'
        ]
        
        self.field_types = {
            'job_title': 'text',
            'company_name': 'text',
            'experience_required': 'text',
            'employment_type': 'select',
            'salary_range': 'text',
            'industry': 'text',
            'location': 'text',
            'department': 'text'
        }
        
        self.validation_patterns = {
            'job_title': r'^[a-zA-Z\s\-\.]+$',
            'company_name': r'^[a-zA-Z\s\-\.&]+$',
            'experience_required': r'^[\d\s\-\+]+(?:years?|yrs?)?$',
            'salary_range': r'^[\$\d,\s\-]+$'
        }
        
        self.error_messages = {
            'job_title': 'Job title is required and should contain only letters, spaces, hyphens, and periods',
            'company_name': 'Company name is required and should contain only letters, spaces, hyphens, periods, and ampersands',
            'experience_required': 'Experience is required and should be in format like "5+ years" or "3-5 years"',
            'employment_type': 'Employment type is required',
            'salary_range': 'Salary range is required and should be in format like "$80,000 - $100,000"'
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            'openai_model': self.openai_model,
            'openai_temperature': self.openai_temperature,
            'rag_enabled': self.rag_enabled,
            'rag_top_k': self.rag_top_k,
            'rag_similarity_threshold': self.rag_similarity_threshold,
            'required_fields': self.required_fields,
            'field_types': self.field_types,
            'validation_patterns': self.validation_patterns,
            'error_messages': self.error_messages
        }
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        if not self.job_descriptions_dir.exists():
            raise ValueError(f"Job descriptions directory does not exist: {self.job_descriptions_dir}")
        
        return True
