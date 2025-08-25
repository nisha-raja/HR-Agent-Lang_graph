"""
Pure Resume Analyzer Agent - Self-contained resume analysis
"""

import os
import json
from typing import Dict, Any, List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from .models import ResumeData, JobDescriptionData, ResumeAnalysisResponse, AnalysisResult
from .config import ResumeAnalyzerConfig
from .utils import ResumeFileManager, ResumeParser, AnalysisScorer

class ResumeAnalysisState(TypedDict):
    """State for the resume analysis workflow"""
    resume_data: ResumeData
    job_description_data: JobDescriptionData
    skills_analysis: Dict[str, Any]
    experience_analysis: Dict[str, Any]
    formatting_analysis: Dict[str, Any]
    overall_score: int
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    final_report: str
    current_step: str
    messages: List[Dict[str, Any]]

class ResumeAnalyzerAgent:
    """Pure Resume Analyzer Agent - Self-contained and deployable independently"""
    
    def __init__(self):
        # Initialize configuration
        self.config = ResumeAnalyzerConfig()
        self.config.validate_config()
        
        # Initialize utilities
        self.file_manager = ResumeFileManager(
            self.config.resumes_dir, 
            self.config.analysis_results_dir
        )
        self.parser = ResumeParser()
        self.scorer = AnalysisScorer(self.config.get_config())
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.config.openai_model,
            temperature=self.config.openai_temperature,
            api_key=self.config.openai_api_key
        )
    
    def analyze_skills(self, state: ResumeAnalysisState) -> ResumeAnalysisState:
        """Analyze skills match between resume and job description"""
        resume_text = state['resume_data'].content
        job_desc_text = state['job_description_data'].content
        
        # Extract skills from resume
        resume_skills = self.parser.extract_skills(resume_text)
        
        # Extract required skills from job description
        job_skills = self.parser.extract_skills(job_desc_text)
        
        # Calculate skills score
        skills_score = self.scorer.calculate_skills_score(resume_skills, job_skills)
        
        # Generate skills analysis
        prompt = f"""
        Analyze the skills match between the candidate's resume and the job requirements.
        
        Resume Skills: {resume_skills}
        Job Requirements: {job_skills}
        Skills Score: {skills_score}/100
        
        Provide a detailed analysis including:
        1. Skills match percentage
        2. Missing critical skills
        3. Additional skills the candidate has
        4. Skills strength assessment
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        state['skills_analysis'] = {
            'resume_skills': resume_skills,
            'job_skills': job_skills,
            'skills_score': skills_score,
            'analysis': response.content
        }
        state['current_step'] = "skills_analyzed"
        
        state['messages'].append({
            "role": "user",
            "content": f"Analyzed skills for {state['resume_data'].candidate_name}"
        })
        
        return state
    
    def analyze_experience(self, state: ResumeAnalysisState) -> ResumeAnalysisState:
        """Analyze experience relevance"""
        resume_text = state['resume_data'].content
        job_desc_text = state['job_description_data'].content
        
        # Extract experience from resume
        resume_experience = self.parser.extract_experience(resume_text)
        
        # Calculate experience score
        experience_score = self.scorer.calculate_experience_score(resume_experience, job_desc_text)
        
        # Generate experience analysis
        prompt = f"""
        Analyze the experience relevance between the candidate's work history and the job requirements.
        
        Resume Experience: {resume_experience}
        Job Requirements: {job_desc_text}
        Experience Score: {experience_score}/100
        
        Provide a detailed analysis including:
        1. Experience relevance assessment
        2. Years of relevant experience
        3. Industry alignment
        4. Role progression analysis
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        state['experience_analysis'] = {
            'resume_experience': resume_experience,
            'experience_score': experience_score,
            'analysis': response.content
        }
        state['current_step'] = "experience_analyzed"
        
        state['messages'].append({
            "role": "user",
            "content": f"Analyzed experience for {state['resume_data'].candidate_name}"
        })
        
        return state
    
    def analyze_formatting(self, state: ResumeAnalysisState) -> ResumeAnalysisState:
        """Analyze resume formatting and presentation"""
        resume_text = state['resume_data'].content
        
        # Calculate formatting score
        formatting_score = self.scorer.calculate_formatting_score(resume_text)
        
        # Generate formatting analysis
        prompt = f"""
        Analyze the formatting and presentation quality of the resume.
        
        Resume Text: {resume_text[:1000]}...
        Formatting Score: {formatting_score}/100
        
        Provide a detailed analysis including:
        1. Structure and organization
        2. Professional presentation
        3. Clarity and readability
        4. Areas for improvement
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        state['formatting_analysis'] = {
            'formatting_score': formatting_score,
            'analysis': response.content
        }
        state['current_step'] = "formatting_analyzed"
        
        state['messages'].append({
            "role": "user",
            "content": f"Analyzed formatting for {state['resume_data'].candidate_name}"
        })
        
        return state
    
    def calculate_overall_score(self, state: ResumeAnalysisState) -> ResumeAnalysisState:
        """Calculate overall score and generate strengths/weaknesses"""
        skills_score = state['skills_analysis']['skills_score']
        experience_score = state['experience_analysis']['experience_score']
        formatting_score = state['formatting_analysis']['formatting_score']
        
        # Calculate overall score
        overall_score = self.scorer.calculate_overall_score(skills_score, experience_score, formatting_score)
        
        # Generate strengths and weaknesses
        prompt = f"""
        Based on the analysis results, identify the candidate's key strengths and areas for improvement.
        
        Skills Score: {skills_score}/100
        Experience Score: {experience_score}/100
        Formatting Score: {formatting_score}/100
        Overall Score: {overall_score}/100
        
        Provide:
        1. Top 3-5 strengths
        2. Top 3-5 areas for improvement
        3. Specific recommendations for enhancement
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Parse response to extract strengths and weaknesses
        content = response.content
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Simple parsing (in a real implementation, you'd use more sophisticated parsing)
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if 'strength' in line.lower():
                current_section = 'strengths'
            elif 'weakness' in line.lower() or 'improvement' in line.lower():
                current_section = 'weaknesses'
            elif 'recommendation' in line.lower():
                current_section = 'recommendations'
            elif line and line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                if current_section == 'strengths':
                    strengths.append(line.lstrip('•-*123456789. '))
                elif current_section == 'weaknesses':
                    weaknesses.append(line.lstrip('•-*123456789. '))
                elif current_section == 'recommendations':
                    recommendations.append(line.lstrip('•-*123456789. '))
        
        state['overall_score'] = overall_score
        state['strengths'] = strengths[:5]  # Limit to top 5
        state['weaknesses'] = weaknesses[:5]  # Limit to top 5
        state['recommendations'] = recommendations[:5]  # Limit to top 5
        state['current_step'] = "scoring_complete"
        
        state['messages'].append({
            "role": "user",
            "content": f"Calculated overall score: {overall_score}/100"
        })
        
        return state
    
    def generate_final_report(self, state: ResumeAnalysisState) -> ResumeAnalysisState:
        """Generate comprehensive final report"""
        prompt = f"""
        Generate a comprehensive resume analysis report for {state['resume_data'].candidate_name}.
        
        Job Title: {state['resume_data'].job_title}
        Company: {state['resume_data'].company_name}
        Overall Score: {state['overall_score']}/100
        
        Skills Analysis: {state['skills_analysis']['analysis']}
        Experience Analysis: {state['experience_analysis']['analysis']}
        Formatting Analysis: {state['formatting_analysis']['analysis']}
        
        Strengths: {state['strengths']}
        Areas for Improvement: {state['weaknesses']}
        Recommendations: {state['recommendations']}
        
        Create a professional, comprehensive report that includes:
        1. Executive summary
        2. Detailed analysis of each component
        3. Overall assessment
        4. Specific recommendations
        5. Next steps
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        state['final_report'] = response.content
        state['current_step'] = "complete"
        
        state['messages'].append({
            "role": "user",
            "content": f"Generated final report for {state['resume_data'].candidate_name}"
        })
        
        return state
    
    def create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(ResumeAnalysisState)
        
        # Add nodes
        workflow.add_node("analyze_skills", self.analyze_skills)
        workflow.add_node("analyze_experience", self.analyze_experience)
        workflow.add_node("analyze_formatting", self.analyze_formatting)
        workflow.add_node("calculate_overall_score", self.calculate_overall_score)
        workflow.add_node("generate_final_report", self.generate_final_report)
        
        # Add edges
        workflow.set_entry_point("analyze_skills")
        workflow.add_edge("analyze_skills", "analyze_experience")
        workflow.add_edge("analyze_experience", "analyze_formatting")
        workflow.add_edge("analyze_formatting", "calculate_overall_score")
        workflow.add_edge("calculate_overall_score", "generate_final_report")
        workflow.add_edge("generate_final_report", END)
        
        return workflow.compile()
    
    def analyze_resume(self, resume_data: ResumeData, job_description_data: JobDescriptionData) -> Dict[str, Any]:
        """Analyze a resume against a job description"""
        try:
            # Initialize state
            state = ResumeAnalysisState(
                resume_data=resume_data,
                job_description_data=job_description_data,
                skills_analysis={},
                experience_analysis={},
                formatting_analysis={},
                overall_score=0,
                strengths=[],
                weaknesses=[],
                recommendations=[],
                final_report="",
                current_step="start",
                messages=[]
            )
            
            # Execute workflow
            final_state = self.create_workflow().invoke(state)
            
            # Convert Pydantic objects to dictionaries for JSON serialization
            return {
                "resume_data": final_state.resume_data.model_dump() if final_state.resume_data else None,
                "job_description_data": final_state.job_description_data.model_dump() if final_state.job_description_data else None,
                "skills_analysis": final_state.skills_analysis,
                "experience_analysis": final_state.experience_analysis,
                "formatting_analysis": final_state.formatting_analysis,
                "overall_score": final_state.overall_score,
                "strengths": final_state.strengths,
                "weaknesses": final_state.weaknesses,
                "recommendations": final_state.recommendations,
                "final_report": final_state.final_report,
                "current_step": final_state.current_step,
                "messages": final_state.messages
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'analysis_failed',
                'message': f'Error analyzing resume: {str(e)}'
            }
    
    def analyze_resume_from_dict(self, resume_data: Dict[str, Any], job_description_data: Dict[str, Any]) -> ResumeAnalysisResponse:
        """Analyze resume from dictionary input"""
        try:
            # Create ResumeData object
            resume_obj = ResumeData(
                content=resume_data['content'],
                candidate_name=resume_data['candidate_name'],
                candidate_email=resume_data.get('candidate_email', ''),
                file_name=resume_data.get('file_name', 'resume.txt')
            )
            
            # Create JobDescriptionData object
            job_desc_obj = JobDescriptionData(
                content=job_description_data['content'],
                job_title=job_description_data['job_title'],
                company_name=job_description_data['company_name']
            )
            
            # Analyze resume
            result = self.analyze_resume(resume_obj, job_desc_obj)
            
            if result.get('success') == False:
                return ResumeAnalysisResponse(
                    success=False,
                    error=result.get('error'),
                    message=result.get('message', 'Analysis failed')
                )
            
            # Save analysis result
            filename = self.file_manager.save_analysis_result(result, resume_obj.file_name)
            
            return ResumeAnalysisResponse(
                success=True,
                analysis_result=result,
                filename=filename,
                message='Resume analysis completed successfully'
            )
            
        except Exception as e:
            return ResumeAnalysisResponse(
                success=False,
                error='analysis_failed',
                message=f'Error analyzing resume: {str(e)}'
            )
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get analysis history"""
        return self.file_manager.load_analysis_results()
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'status': 'healthy',
            'config': self.config.get_config(),
            'analysis_history_count': len(self.get_analysis_history())
        }
