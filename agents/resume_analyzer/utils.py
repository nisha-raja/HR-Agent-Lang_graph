"""
Utilities for Resume Analyzer Agent
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
import PyPDF2
from docx import Document

class ResumeFileManager:
    """File management utilities for Resume Analyzer"""
    
    def __init__(self, resumes_dir: Path, analysis_results_dir: Path):
        self.resumes_dir = resumes_dir
        self.analysis_results_dir = analysis_results_dir
        self.resumes_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_results_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")
    
    def extract_text_from_file(self, file_path: Path) -> str:
        """Extract text from various file formats"""
        if file_path.suffix.lower() == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif file_path.suffix.lower() in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            raise Exception(f"Unsupported file format: {file_path.suffix}")
    
    def save_analysis_result(self, analysis_data: Dict[str, Any], filename: str) -> str:
        """Save analysis result to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_filename = f"analysis_{filename}_{timestamp}.json"
            result_path = self.analysis_results_dir / result_filename
            
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
            return result_filename
            
        except Exception as e:
            raise Exception(f"Error saving analysis result: {str(e)}")
    
    def load_analysis_results(self) -> List[Dict[str, Any]]:
        """Load all analysis results from directory"""
        analysis_results = []
        
        try:
            for file_path in self.analysis_results_dir.glob("analysis_*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    result['filename'] = file_path.name
                    analysis_results.append(result)
            
            return analysis_results
            
        except Exception as e:
            print(f"Warning: Error loading analysis results: {e}")
            return []

class ResumeParser:
    """Resume parsing utilities"""
    
    @staticmethod
    def extract_contact_info(text: str) -> Dict[str, str]:
        """Extract contact information from resume text"""
        contact_info = {
            'name': '',
            'email': '',
            'phone': '',
            'location': ''
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Extract phone
        phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = ''.join(phones[0])
        
        # Extract location (basic pattern)
        location_pattern = r'([A-Z][a-z]+(?:[\s,]+[A-Z][a-z]+)*),\s*([A-Z]{2})'
        locations = re.findall(location_pattern, text)
        if locations:
            contact_info['location'] = f"{locations[0][0]}, {locations[0][1]}"
        
        return contact_info
    
    @staticmethod
    def extract_skills(text: str) -> List[str]:
        """Extract skills from resume text"""
        # Common skill keywords
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'sql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'docker',
            'kubernetes', 'git', 'agile', 'scrum', 'machine learning', 'ai',
            'data analysis', 'excel', 'powerpoint', 'word', 'photoshop',
            'illustrator', 'figma', 'sketch', 'html', 'css', 'php', 'c++',
            'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'typescript'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))
    
    @staticmethod
    def extract_experience(text: str) -> List[Dict[str, str]]:
        """Extract work experience from resume text"""
        experience = []
        
        # Look for common experience patterns
        lines = text.split('\n')
        current_experience = {}
        
        for line in lines:
            line = line.strip()
            
            # Look for job titles
            if any(keyword in line.lower() for keyword in ['engineer', 'developer', 'manager', 'analyst', 'specialist']):
                if current_experience:
                    experience.append(current_experience)
                current_experience = {'title': line}
            
            # Look for company names
            elif any(keyword in line.lower() for keyword in ['inc', 'corp', 'llc', 'ltd', 'company']):
                if current_experience:
                    current_experience['company'] = line
            
            # Look for dates
            elif re.search(r'\d{4}', line):
                if current_experience:
                    current_experience['dates'] = line
        
        if current_experience:
            experience.append(current_experience)
        
        return experience

class AnalysisScorer:
    """Scoring utilities for resume analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        self.analysis_criteria = config['analysis_criteria']
        self.scoring_ranges = config['scoring_ranges']
    
    def calculate_skills_score(self, resume_skills: List[str], job_requirements: List[str]) -> int:
        """Calculate skills match score"""
        if not job_requirements:
            return 50
        
        matched_skills = set(resume_skills) & set(job_requirements)
        match_percentage = len(matched_skills) / len(job_requirements) * 100
        
        return min(100, int(match_percentage))
    
    def calculate_experience_score(self, resume_experience: List[Dict], job_requirements: str) -> int:
        """Calculate experience relevance score"""
        # Simple scoring based on experience length and relevance
        total_years = 0
        relevant_experience = 0
        
        for exp in resume_experience:
            # Extract years from experience
            if 'dates' in exp:
                dates = exp['dates']
                # Simple year extraction
                years = re.findall(r'\d{4}', dates)
                if len(years) >= 2:
                    total_years += int(years[1]) - int(years[0])
            
            # Check relevance
            if any(keyword in exp.get('title', '').lower() for keyword in job_requirements.lower().split()):
                relevant_experience += 1
        
        # Score based on total years and relevance
        years_score = min(100, total_years * 10)
        relevance_score = min(100, relevant_experience * 25)
        
        return (years_score + relevance_score) // 2
    
    def calculate_formatting_score(self, text: str) -> int:
        """Calculate formatting and presentation score"""
        score = 50  # Base score
        
        # Check for proper sections
        sections = ['experience', 'education', 'skills', 'summary']
        for section in sections:
            if section in text.lower():
                score += 10
        
        # Check for bullet points
        if '•' in text or '-' in text or '*' in text:
            score += 10
        
        # Check for proper spacing
        if '\n\n' in text:
            score += 10
        
        # Check for professional language
        professional_words = ['developed', 'implemented', 'managed', 'created', 'designed']
        if any(word in text.lower() for word in professional_words):
            score += 10
        
        return min(100, score)
    
    def calculate_overall_score(self, skills_score: int, experience_score: int, formatting_score: int) -> int:
        """Calculate overall score"""
        weights = self.analysis_criteria
        
        overall_score = (
            skills_score * weights['skills_weight'] +
            experience_score * weights['experience_weight'] +
            formatting_score * weights['formatting_weight']
        )
        
        return int(overall_score)
    
    def get_score_category(self, score: int) -> str:
        """Get score category"""
        for category, (min_score, max_score) in self.scoring_ranges.items():
            if min_score <= score <= max_score:
                return category
        return 'poor'
