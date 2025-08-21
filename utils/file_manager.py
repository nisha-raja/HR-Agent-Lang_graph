"""
File Manager Utility
Handles all file operations for job descriptions, resumes, and analysis results
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

class FileManager:
    """Manages file operations for the HR Agent Suite"""
    
    def __init__(self):
        # Define base directories
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.job_descriptions_dir = self.data_dir / "job_descriptions"
        self.resumes_dir = self.data_dir / "resumes"
        self.analysis_results_dir = self.data_dir / "analysis_results"
        
        # Ensure directories exist
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            self.data_dir,
            self.job_descriptions_dir,
            self.resumes_dir,
            self.analysis_results_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_job_description(self, job_details: Dict[str, Any], description: str) -> Tuple[str, str]:
        """Save job description and metadata"""
        try:
            # Create filename
            job_title = job_details.get('job_title', 'Unknown')
            company_name = job_details.get('company_name', 'Unknown')
            filename = f"{job_title.replace(' ', '_')}_{company_name.replace(' ', '_')}_job_description.txt"
            filepath = self.job_descriptions_dir / filename
            
            # Save job description
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(description)
            
            # Create and save metadata
            metadata = {
                "job_title": job_title,
                "company_name": company_name,
                "experience_required": job_details.get('experience_required', 'Not specified'),
                "employment_type": job_details.get('employment_type', 'Not specified'),
                "salary_range": job_details.get('salary_range', 'Not specified'),
                "industry": job_details.get('industry', 'Not specified'),
                "location": job_details.get('location', 'Not specified'),
                "department": job_details.get('department', 'Not specified'),
                "description_file": filename,
                "created_at": datetime.now().isoformat()
            }
            
            metadata_filename = f"{job_title.replace(' ', '_')}_{company_name.replace(' ', '_')}_metadata.json"
            metadata_filepath = self.job_descriptions_dir / metadata_filename
            
            with open(metadata_filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            return str(filepath), str(metadata_filepath)
            
        except Exception as e:
            raise Exception(f"Failed to save job description: {str(e)}")
    
    def load_job_description(self, filename: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Load job description content and metadata"""
        try:
            filepath = self.job_descriptions_dir / filename
            
            # Load job description content
            if not filepath.exists():
                return None, None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                jd_content = f.read()
            
            # Load metadata
            metadata_filename = filename.replace('_job_description.txt', '_metadata.json')
            metadata_filepath = self.job_descriptions_dir / metadata_filename
            
            jd_metadata = None
            if metadata_filepath.exists():
                with open(metadata_filepath, 'r', encoding='utf-8') as f:
                    jd_metadata = json.load(f)
            else:
                # Create basic metadata if not available
                jd_metadata = {
                    'job_title': 'Unknown Position',
                    'company_name': 'Unknown Company',
                    'experience_required': 'Not specified',
                    'employment_type': 'Not specified',
                    'salary_range': 'Not specified',
                    'industry': 'Not specified',
                    'location': 'Not specified',
                    'department': 'Not specified'
                }
            
            return jd_content, jd_metadata
            
        except Exception as e:
            return None, None
    
    def list_job_descriptions(self) -> List[str]:
        """List all available job description files"""
        try:
            jd_files = []
            for file in self.job_descriptions_dir.glob('*_job_description.txt'):
                jd_files.append(file.name)
            return sorted(jd_files)
        except Exception as e:
            return []
    
    def delete_job_description(self, filename: str) -> bool:
        """Delete a job description and its metadata"""
        try:
            filepath = self.job_descriptions_dir / filename
            metadata_filename = filename.replace('_job_description.txt', '_metadata.json')
            metadata_filepath = self.job_descriptions_dir / metadata_filename
            
            # Delete job description file
            if filepath.exists():
                filepath.unlink()
            
            # Delete metadata file
            if metadata_filepath.exists():
                metadata_filepath.unlink()
            
            return True
            
        except Exception as e:
            return False
    
    def save_resume(self, resume_data: Dict[str, Any], filename: str) -> str:
        """Save resume file"""
        try:
            # Get candidate name from resume data
            candidate_name = resume_data.get('candidate_name', 'Unknown')
            
            # Create a better filename using candidate name and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_candidate_name = candidate_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            new_filename = f"{safe_candidate_name}_resume_{timestamp}.txt"
            
            filepath = self.resumes_dir / new_filename
            
            # Save resume content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(resume_data.get('content', ''))
            
            return str(filepath)
            
        except Exception as e:
            raise Exception(f"Failed to save resume: {str(e)}")
    
    def load_resume(self, filename: str) -> Optional[str]:
        """Load resume content"""
        try:
            filepath = self.resumes_dir / filename
            
            if not filepath.exists():
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            return None
    
    def list_resumes(self) -> List[str]:
        """List all available resume files"""
        try:
            resume_files = []
            for file in self.resumes_dir.glob('*.txt'):
                resume_files.append(file.name)
            return sorted(resume_files)
        except Exception as e:
            return []
    
    def save_analysis_result(self, analysis_result: Dict[str, Any], candidate_name: str, candidate_email: str = None) -> str:
        """Save analysis result"""
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{candidate_name.replace(' ', '_')}_analysis_{timestamp}.json"
            filepath = self.analysis_results_dir / filename
            
            # Add metadata to analysis result
            analysis_result['metadata'] = {
                'candidate_name': candidate_name,
                'candidate_email': candidate_email,
                'created_at': datetime.now().isoformat(),
                'analysis_file': filename
            }
            
            # Save analysis result
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2)
            
            return str(filepath)
            
        except Exception as e:
            raise Exception(f"Failed to save analysis result: {str(e)}")
    
    def load_analysis_result(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load analysis result"""
        try:
            filepath = self.analysis_results_dir / filename
            
            if not filepath.exists():
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            return None
    
    def list_analysis_results(self) -> List[str]:
        """List all available analysis result files"""
        try:
            analysis_files = []
            for file in self.analysis_results_dir.glob('*.json'):
                analysis_files.append(file.name)
            return sorted(analysis_files)
        except Exception as e:
            return []
    
    def delete_analysis_result(self, filename: str) -> bool:
        """Delete an analysis result file"""
        try:
            filepath = self.analysis_results_dir / filename
            
            if filepath.exists():
                filepath.unlink()
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """Clean up files older than specified days"""
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            deleted_count = 0
            
            # Clean up old files in all directories
            directories = [self.job_descriptions_dir, self.resumes_dir, self.analysis_results_dir]
            
            for directory in directories:
                for file in directory.glob('*'):
                    if file.is_file() and file.stat().st_mtime < cutoff_time:
                        file.unlink()
                        deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            return 0
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information for all directories"""
        try:
            info = {}
            
            for name, directory in [
                ('job_descriptions', self.job_descriptions_dir),
                ('resumes', self.resumes_dir),
                ('analysis_results', self.analysis_results_dir)
            ]:
                file_count = len(list(directory.glob('*')))
                total_size = sum(f.stat().st_size for f in directory.glob('*') if f.is_file())
                
                info[name] = {
                    'file_count': file_count,
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2)
                }
            
            return info
            
        except Exception as e:
            return {}
