"""
Utilities for JD Generator Agent
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
from difflib import SequenceMatcher

class JDFileManager:
    """File management utilities for JD Generator"""
    
    def __init__(self, job_descriptions_dir: Path):
        self.job_descriptions_dir = job_descriptions_dir
        self.job_descriptions_dir.mkdir(parents=True, exist_ok=True)
    
    def save_job_description(self, job_details: Dict[str, Any], description: str) -> Tuple[str, str]:
        """Save job description and metadata to files"""
        try:
            # Create timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create filename
            job_title_clean = re.sub(r'[^\w\s-]', '', job_details['job_title']).replace(' ', '_')
            filename = f"{job_title_clean}_{timestamp}_job_description.txt"
            metadata_filename = f"{job_title_clean}_{timestamp}_metadata.json"
            
            # Save job description
            job_description_path = self.job_descriptions_dir / filename
            with open(job_description_path, 'w', encoding='utf-8') as f:
                f.write(description)
            
            # Save metadata
            metadata = {
                'job_title': job_details['job_title'],
                'company_name': job_details['company_name'],
                'experience_required': job_details['experience_required'],
                'employment_type': job_details['employment_type'],
                'salary_range': job_details['salary_range'],
                'industry': job_details.get('industry', 'Technology'),
                'location': job_details.get('location', 'Remote'),
                'department': job_details.get('department', 'General'),
                'generated_at': datetime.now().isoformat(),
                'filename': filename
            }
            
            metadata_path = self.job_descriptions_dir / metadata_filename
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return filename, metadata_filename
            
        except Exception as e:
            raise Exception(f"Error saving job description: {str(e)}")
    
    def load_job_descriptions(self) -> List[Dict[str, Any]]:
        """Load all job descriptions from directory"""
        job_descriptions = []
        
        try:
            for file_path in self.job_descriptions_dir.glob("*_job_description.txt"):
                # Find corresponding metadata file
                metadata_filename = file_path.stem.replace('_job_description', '_metadata') + '.json'
                metadata_path = self.job_descriptions_dir / metadata_filename
                
                # Read job description content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Read metadata if available
                metadata = {}
                if metadata_path.exists():
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                
                job_descriptions.append({
                    'filename': file_path.name,
                    'content': content,
                    'metadata': metadata
                })
            
            return job_descriptions
            
        except Exception as e:
            print(f"Warning: Error loading job descriptions: {e}")
            return []
    
    def delete_job_description(self, filename: str) -> bool:
        """Delete job description and its metadata"""
        try:
            # Delete job description file
            job_desc_path = self.job_descriptions_dir / filename
            if job_desc_path.exists():
                job_desc_path.unlink()
            
            # Delete metadata file
            metadata_filename = filename.replace('_job_description.txt', '_metadata.json')
            metadata_path = self.job_descriptions_dir / metadata_filename
            if metadata_path.exists():
                metadata_path.unlink()
            
            return True
            
        except Exception as e:
            print(f"Error deleting job description: {e}")
            return False

class JDValidator:
    """Validation utilities for JD Generator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.required_fields = config['required_fields']
        self.validation_patterns = config['validation_patterns']
        self.error_messages = config['error_messages']
    
    def validate_job_details(self, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Validate job details"""
        missing_fields = []
        
        for field in self.required_fields:
            if not job_details.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            return {
                'valid': False,
                'missing_fields': missing_fields,
                'message': f"Missing required fields: {', '.join(missing_fields)}"
            }
        
        # Validate patterns
        for field, pattern in self.validation_patterns.items():
            if field in job_details and job_details[field]:
                if not re.match(pattern, job_details[field]):
                    return {
                        'valid': False,
                        'message': self.error_messages.get(field, f"Invalid format for {field}")
                    }
        
        return {
            'valid': True,
            'message': "Job details are valid"
        }

class RAGUtils:
    """RAG utilities for JD Generator"""
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    @staticmethod
    def extract_relevant_sections(content: str) -> str:
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
