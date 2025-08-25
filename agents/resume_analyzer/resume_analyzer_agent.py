"""
Resume Analysis Agent using LangGraph
A sophisticated workflow-based agent for analyzing resumes against job descriptions
"""

import os
import json
from typing import Dict, Any, List, TypedDict, Annotated
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ResumeData(BaseModel):
    """Model for resume input data"""
    content: str = Field(description="The full content of the resume")
    candidate_name: str = Field(description="Name of the candidate")
    candidate_email: str = Field(description="Email of the candidate", default="")
    file_name: str = Field(description="Name of the resume file")

class JobDescriptionData(BaseModel):
    """Model for job description data"""
    content: str = Field(description="The full content of the job description")
    job_title: str = Field(description="Title of the position")
    company_name: str = Field(description="Name of the hiring company")

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

class LangGraphResumeAnalyzer:
    """LangGraph-based Resume Analysis Agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,  # Lower temperature for more consistent analysis
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def list_available_job_descriptions(self) -> List[str]:
        """List available job description files"""
        job_description_files = []
        for file in os.listdir('.'):
            if file.endswith('_job_description.txt'):
                job_description_files.append(file)
        return job_description_files
    
    def load_job_description_from_file(self, filename: str) -> tuple[str, str, str]:
        """Load job description from file and extract metadata"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to find metadata file
            metadata_filename = filename.replace('_job_description.txt', '_metadata.json')
            if os.path.exists(metadata_filename):
                with open(metadata_filename, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                job_title = metadata.get('job_title', 'Unknown')
                company_name = metadata.get('company_name', 'Unknown')
            else:
                # Extract from filename if no metadata
                parts = filename.replace('_job_description.txt', '').split('_')
                if len(parts) >= 2:
                    job_title = ' '.join(parts[:-1])
                    company_name = parts[-1]
                else:
                    job_title = "Unknown"
                    company_name = "Unknown"
            
            return content, job_title, company_name
        except Exception as e:
            print(f"Error loading job description: {e}")
            return "", "Unknown", "Unknown"
    
    def get_input_data(self) -> tuple[ResumeData, JobDescriptionData]:
        """Get resume and job description data from user"""
        print("📋 Resume Analysis Agent")
        print("=" * 50)
        print("Please provide the resume and job description for analysis:")
        print()
        
        # Check for available job descriptions
        available_jds = self.list_available_job_descriptions()
        
        if available_jds:
            print("📄 Available Job Descriptions:")
            for i, jd_file in enumerate(available_jds, 1):
                print(f"{i}. {jd_file}")
            print("0. Enter job description manually")
            
            choice = input("\nSelect job description (0-{}): ".format(len(available_jds))).strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(available_jds):
                selected_jd = available_jds[int(choice) - 1]
                jd_content, job_title, company_name = self.load_job_description_from_file(selected_jd)
                print(f"\n✅ Loaded: {job_title} at {company_name}")
            else:
                # Manual input
                job_title = input("Job Title: ").strip()
                company_name = input("Company Name: ").strip()
                
                print("\nPaste the job description content below (press Enter twice when done):")
                jd_lines = []
                while True:
                    line = input()
                    if line == "" and jd_lines and jd_lines[-1] == "":
                        break
                    jd_lines.append(line)
                
                jd_content = "\n".join(jd_lines[:-1])  # Remove the last empty line
        else:
            # No saved job descriptions, manual input
            job_title = input("Job Title: ").strip()
            company_name = input("Company Name: ").strip()
            
            print("\nPaste the job description content below (press Enter twice when done):")
            jd_lines = []
            while True:
                line = input()
                if line == "" and jd_lines and jd_lines[-1] == "":
                    break
                jd_lines.append(line)
            
            jd_content = "\n".join(jd_lines[:-1])  # Remove the last empty line
        
        # Get resume data
        print("\n📄 RESUME INPUT:")
        print("-" * 20)
        candidate_name = input("Candidate Name: ").strip()
        file_name = input("Resume File Name: ").strip()
        
        print("\nPaste the resume content below (press Enter twice when done):")
        resume_lines = []
        while True:
            line = input()
            if line == "" and resume_lines and resume_lines[-1] == "":
                break
            resume_lines.append(line)
        
        resume_content = "\n".join(resume_lines[:-1])  # Remove the last empty line
        
        resume_data = ResumeData(
            content=resume_content,
            candidate_name=candidate_name,
            file_name=file_name
        )
        
        job_description_data = JobDescriptionData(
            content=jd_content,
            job_title=job_title,
            company_name=company_name
        )
        
        return resume_data, job_description_data
    
    def analyze_skills_match(self, state: ResumeAnalysisState) -> ResumeAnalysisState:
        """Analyze skills match between resume and job description"""
        
        prompt = f"""
        Analyze the skills match between the candidate's resume and the job description.
        
        RESUME CONTENT:
        {state['resume_data'].content}
        
        JOB DESCRIPTION:
        {state['job_description_data'].content}
        
        JOB TITLE: {state['job_description_data'].job_title}
        COMPANY: {state['job_description_data'].company_name}
        CANDIDATE: {state['resume_data'].candidate_name}
        
        IMPORTANT: If the resume content is insufficient (less than 50 characters) or contains obvious placeholder text like "test", "sample", etc., provide a lower score and explain why the analysis may be limited.
        
        Please analyze:
        1. Required skills mentioned in the job description
        2. Skills demonstrated in the resume
        3. Skill relevance and match percentage
        4. Missing critical skills
        5. Additional skills that are beneficial
        
        Provide your analysis in JSON format:
        {{
            "required_skills": ["skill1", "skill2", ...],
            "candidate_skills": ["skill1", "skill2", ...],
            "matching_skills": ["skill1", "skill2", ...],
            "missing_skills": ["skill1", "skill2", ...],
            "skill_match_percentage": 85,
            "skill_score": 85,
            "analysis": "Detailed analysis of skills match..."
        }}
        
        SCORING GUIDELINES:
        - 0-20: Very insufficient content or obvious placeholder text
        - 21-40: Limited skills mentioned
        - 41-60: Some relevant skills but gaps
        - 61-80: Good skills match with minor gaps
        - 81-100: Excellent skills alignment
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        try:
            skills_analysis = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            skills_analysis = {
                "required_skills": [],
                "candidate_skills": [],
                "matching_skills": [],
                "missing_skills": [],
                "skill_match_percentage": 0,
                "skill_score": 0,
                "analysis": "Error parsing analysis. Please provide more detailed resume content."
            }
        
        # Additional validation for low-quality content - only apply for very short content
        if len(state['resume_data'].content.strip()) < 50:
            skills_analysis['skill_match_percentage'] = max(0, skills_analysis.get('skill_match_percentage', 0) - 30)
            skills_analysis['skill_score'] = max(0, skills_analysis.get('skill_score', 0) - 30)
            skills_analysis['analysis'] += " Score reduced due to insufficient content length."
        
        state['skills_analysis'] = skills_analysis
        state['current_step'] = "skills_analyzed"
        
        state['messages'].append({
            "role": "user",
            "content": f"Analyzed skills match for {state['resume_data'].candidate_name}"
        })
        
        return state
    
    def analyze_experience_relevance(self, state: ResumeAnalysisState) -> ResumeAnalysisState:
        """Analyze experience relevance to the job requirements"""
        
        prompt = f"""
        Analyze the experience relevance between the candidate's resume and the job description.
        
        RESUME CONTENT:
        {state['resume_data'].content}
        
        JOB DESCRIPTION:
        {state['job_description_data'].content}
        
        JOB TITLE: {state['job_description_data'].job_title}
        COMPANY: {state['job_description_data'].company_name}
        CANDIDATE: {state['resume_data'].candidate_name}
        
        IMPORTANT: If the resume content is insufficient (less than 50 characters) or contains obvious placeholder text like "test", "sample", etc., provide a lower score and explain why the analysis may be limited.
        
        Please analyze:
        1. Required experience level in the job description
        2. Candidate's relevant experience
        3. Experience relevance and alignment
        4. Experience gaps or overqualification
        5. Project and role relevance
        
        Provide your analysis in JSON format:
        {{
            "required_experience": "5+ years",
            "candidate_experience": "3 years",
            "experience_relevance": "High/Medium/Low",
            "experience_score": 80,
            "relevant_projects": ["project1", "project2", ...],
            "experience_gaps": ["gap1", "gap2", ...],
            "analysis": "Detailed analysis of experience relevance..."
        }}
        
        SCORING GUIDELINES:
        - 0-20: Very insufficient content or obvious placeholder text
        - 21-40: Limited experience information
        - 41-60: Some experience but unclear relevance
        - 61-80: Good experience alignment
        - 81-100: Excellent experience match
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        try:
            experience_analysis = json.loads(response.content)
        except json.JSONDecodeError:
            experience_analysis = {
                "required_experience": "Unknown",
                "candidate_experience": "Unknown",
                "experience_relevance": "Low",
                "experience_score": 0,
                "relevant_projects": [],
                "experience_gaps": [],
                "analysis": "Error parsing analysis. Please provide more detailed resume content."
            }
        
        # Additional validation for low-quality content - only apply for very short content
        if len(state['resume_data'].content.strip()) < 50:
            experience_analysis['experience_score'] = max(0, experience_analysis.get('experience_score', 0) - 30)
            experience_analysis['analysis'] += " Score reduced due to insufficient content length."
        
        state['experience_analysis'] = experience_analysis
        state['current_step'] = "experience_analyzed"
        
        state['messages'].append({
            "role": "user",
            "content": f"Analyzed experience relevance for {state['resume_data'].candidate_name}"
        })
        
        return state
    
    def analyze_resume_formatting(self, state: ResumeAnalysisState) -> ResumeAnalysisState:
        """Analyze resume formatting and presentation"""
        
        prompt = f"""
        Analyze the formatting and presentation quality of the resume.
        
        RESUME CONTENT:
        {state['resume_data'].content}
        
        CANDIDATE: {state['resume_data'].candidate_name}
        
        IMPORTANT: If the resume content is insufficient (less than 50 characters) or contains obvious placeholder text like "test", "sample", etc., provide a lower score and explain why the analysis may be limited.
        
        Please analyze:
        1. Overall structure and organization
        2. Clarity and readability
        3. Professional presentation
        4. Grammar and spelling
        5. Formatting consistency
        6. Use of action verbs and quantifiable achievements
        
        Provide your analysis in JSON format:
        {{
            "structure_score": 85,
            "clarity_score": 80,
            "professionalism_score": 90,
            "grammar_score": 95,
            "formatting_score": 85,
            "overall_formatting_score": 87,
            "strengths": ["strength1", "strength2", ...],
            "weaknesses": ["weakness1", "weakness2", ...],
            "analysis": "Detailed analysis of formatting..."
        }}
        
        SCORING GUIDELINES:
        - 0-20: Very insufficient content or obvious placeholder text
        - 21-40: Poor formatting and structure
        - 41-60: Basic formatting with issues
        - 61-80: Good formatting and presentation
        - 81-100: Excellent formatting and structure
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        try:
            formatting_analysis = json.loads(response.content)
        except json.JSONDecodeError:
            formatting_analysis = {
                "structure_score": 0,
                "clarity_score": 0,
                "professionalism_score": 0,
                "grammar_score": 0,
                "formatting_score": 0,
                "overall_formatting_score": 0,
                "strengths": [],
                "weaknesses": ["Insufficient content for proper formatting analysis"],
                "analysis": "Error parsing analysis. Please provide more detailed resume content."
            }
        
        # Additional validation for low-quality content - only apply for very short content
        if len(state['resume_data'].content.strip()) < 50:
            formatting_analysis['overall_formatting_score'] = max(0, formatting_analysis.get('overall_formatting_score', 0) - 30)
            formatting_analysis['analysis'] += " Score reduced due to insufficient content length."
        
        state['formatting_analysis'] = formatting_analysis
        state['current_step'] = "formatting_analyzed"
        
        state['messages'].append({
            "role": "user",
            "content": f"Analyzed formatting for {state['resume_data'].candidate_name}"
        })
        
        return state
    
    def calculate_overall_score(self, state: ResumeAnalysisState) -> ResumeAnalysisState:
        """Calculate overall score based on all analyses"""
        
        skills_score = state['skills_analysis'].get('skill_score', 70)
        experience_score = state['experience_analysis'].get('experience_score', 75)
        formatting_score = state['formatting_analysis'].get('overall_formatting_score', 80)
        
        # Weighted scoring: Skills (40%), Experience (35%), Formatting (25%)
        overall_score = int(
            (skills_score * 0.4) + 
            (experience_score * 0.35) + 
            (formatting_score * 0.25)
        )
        
        state['overall_score'] = overall_score
        state['current_step'] = "score_calculated"
        
        return state
    
    def identify_strengths_weaknesses(self, state: ResumeAnalysisState) -> ResumeAnalysisState:
        """Identify strengths and weaknesses based on analysis"""
        
        prompt = f"""
        Based on the analysis results, identify the candidate's strengths and weaknesses.
        
        SKILLS ANALYSIS: {state['skills_analysis']}
        EXPERIENCE ANALYSIS: {state['experience_analysis']}
        FORMATTING ANALYSIS: {state['formatting_analysis']}
        OVERALL SCORE: {state['overall_score']}
        
        CANDIDATE: {state['resume_data'].candidate_name}
        JOB: {state['job_description_data'].job_title} at {state['job_description_data'].company_name}
        
        Please provide:
        1. Top 3-5 strengths that make the candidate suitable for this role
        2. Top 3-5 weaknesses or areas for improvement
        3. Keep the tone professional and constructive
        
        Provide your analysis in JSON format:
        {{
            "strengths": ["strength1", "strength2", "strength3", ...],
            "weaknesses": ["weakness1", "weakness2", "weakness3", ...]
        }}
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        try:
            analysis_result = json.loads(response.content)
            state['strengths'] = analysis_result.get('strengths', [])
            state['weaknesses'] = analysis_result.get('weaknesses', [])
        except json.JSONDecodeError:
            state['strengths'] = ["Good technical skills", "Relevant experience"]
            state['weaknesses'] = ["Could improve formatting", "Some skills gaps"]
        
        state['current_step'] = "strengths_weaknesses_identified"
        
        return state
    
    def generate_recommendations(self, state: ResumeAnalysisState) -> ResumeAnalysisState:
        """Generate personalized recommendations for improvement"""
        
        prompt = f"""
        Generate personalized recommendations for the candidate to improve their resume and job application.
        
        CANDIDATE: {state['resume_data'].candidate_name}
        JOB: {state['job_description_data'].job_title} at {state['job_description_data'].company_name}
        
        SKILLS ANALYSIS: {state['skills_analysis']}
        EXPERIENCE ANALYSIS: {state['experience_analysis']}
        FORMATTING ANALYSIS: {state['formatting_analysis']}
        STRENGTHS: {state['strengths']}
        WEAKNESSES: {state['weaknesses']}
        OVERALL SCORE: {state['overall_score']}
        
        Please provide 5-7 specific, actionable recommendations for:
        1. Skills development
        2. Experience enhancement
        3. Resume formatting improvements
        4. Application strategy
        
        Provide your recommendations in JSON format:
        {{
            "recommendations": ["recommendation1", "recommendation2", ...]
        }}
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        try:
            recommendations_result = json.loads(response.content)
            state['recommendations'] = recommendations_result.get('recommendations', [])
        except json.JSONDecodeError:
            state['recommendations'] = [
                "Improve resume formatting",
                "Add more quantifiable achievements",
                "Develop missing technical skills"
            ]
        
        state['current_step'] = "recommendations_generated"
        
        return state
    
    def compile_final_report(self, state: ResumeAnalysisState) -> ResumeAnalysisState:
        """Compile the final analysis report"""
        
        prompt = f"""
        Compile a comprehensive, professional resume analysis report.
        
        CANDIDATE: {state['resume_data'].candidate_name}
        JOB: {state['job_description_data'].job_title} at {state['job_description_data'].company_name}
        
        OVERALL SCORE: {state['overall_score']}/100
        
        SKILLS ANALYSIS: {state['skills_analysis']}
        EXPERIENCE ANALYSIS: {state['experience_analysis']}
        FORMATTING ANALYSIS: {state['formatting_analysis']}
        
        STRENGTHS: {state['strengths']}
        WEAKNESSES: {state['weaknesses']}
        RECOMMENDATIONS: {state['recommendations']}
        
        Create a professional report with:
        1. Executive Summary
        2. Detailed Analysis (Skills, Experience, Formatting)
        3. Strengths and Weaknesses
        4. Recommendations for Improvement
        5. Overall Assessment
        
        Format the report professionally with clear sections and bullet points.
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
        """Create the LangGraph workflow for resume analysis"""
        
        workflow = StateGraph(ResumeAnalysisState)
        
        # Add nodes
        workflow.add_node("analyze_skills", self.analyze_skills_match)
        workflow.add_node("analyze_experience", self.analyze_experience_relevance)
        workflow.add_node("analyze_formatting", self.analyze_resume_formatting)
        workflow.add_node("calculate_score", self.calculate_overall_score)
        workflow.add_node("identify_sw", self.identify_strengths_weaknesses)
        workflow.add_node("generate_recs", self.generate_recommendations)
        workflow.add_node("compile_report", self.compile_final_report)
        
        # Define the workflow
        workflow.set_entry_point("analyze_skills")
        workflow.add_edge("analyze_skills", "analyze_experience")
        workflow.add_edge("analyze_experience", "analyze_formatting")
        workflow.add_edge("analyze_formatting", "calculate_score")
        workflow.add_edge("calculate_score", "identify_sw")
        workflow.add_edge("identify_sw", "generate_recs")
        workflow.add_edge("generate_recs", "compile_report")
        workflow.add_edge("compile_report", END)
        
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
            
            # Execute the workflow
            final_state = self.create_workflow().invoke(state)
            
            # Convert Pydantic objects to dictionaries for JSON serialization
            serializable_state = {}
            for key, value in final_state.items():
                if key == 'resume_data':
                    serializable_state[key] = {
                        'content': value.content,
                        'candidate_name': value.candidate_name,
                        'candidate_email': value.candidate_email,
                        'file_name': value.file_name
                    }
                elif key == 'job_description_data':
                    serializable_state[key] = {
                        'content': value.content,
                        'job_title': value.job_title,
                        'company_name': value.company_name
                    }
                else:
                    serializable_state[key] = value
            
            return serializable_state
            
        except Exception as e:
            print(f"Error analyzing resume: {e}")
            return {
                'overall_score': 0,
                'error': str(e)
            }
    
    def analyze_resume_with_save(self, resume_data: Dict[str, Any], job_description_data: Dict[str, Any], file_manager) -> Dict[str, Any]:
        """Analyze resume and save results using file manager"""
        try:
            # Convert dicts to objects
            resume_obj = ResumeData(**resume_data)
            jd_obj = JobDescriptionData(**job_description_data)
            
            # Save resume file first
            resume_filename = file_manager.save_resume(resume_data, resume_data.get('file_name', 'resume.txt'))
            
            # Analyze resume
            analysis_result = self.analyze_resume(resume_obj, jd_obj)
            
            # Save analysis result
            candidate_email = getattr(resume_obj, 'candidate_email', None)
            analysis_filename = file_manager.save_analysis_result(analysis_result, resume_obj.candidate_name, candidate_email)
            
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
    
    def validate_inputs(self, resume_data: ResumeData, job_description_data: JobDescriptionData) -> Dict[str, Any]:
        """Validate resume and job description inputs"""
        
        # Check resume content length
        if len(resume_data.content.strip()) < 50:
            return {
                'valid': False,
                'message': 'Resume content is too short. Please provide at least 50 characters of detailed resume content.'
            }
        
        # Check for meaningful content (not just repeated words)
        content_words = resume_data.content.lower().split()
        if len(set(content_words)) < 5:
            return {
                'valid': False,
                'message': 'Resume content lacks variety. Please provide more diverse and detailed information about your experience, skills, and qualifications.'
            }
        
        # Check job description content
        if len(job_description_data.content.strip()) < 30:
            return {
                'valid': False,
                'message': 'Job description is too short. Please provide a more detailed job description.'
            }
        
        # Check for very obvious placeholder text (repeated patterns)
        placeholder_indicators = ['test test test', 'sample sample sample', 'placeholder placeholder', 'dummy dummy dummy']
        resume_lower = resume_data.content.lower()
        if any(indicator in resume_lower for indicator in placeholder_indicators):
            return {
                'valid': False,
                'message': 'Resume appears to contain obvious placeholder text. Please provide actual resume content.'
            }
        
        return {'valid': True, 'message': 'Input validation passed'}

def main():
    """Main function to run the LangGraph Resume Analysis Agent"""
    
    try:
        # Initialize the agent
        analyzer = LangGraphResumeAnalyzer()
        
        # Get input data from user
        resume_data, job_description_data = analyzer.get_input_data()
        
        print("\n" + "=" * 50)
        print("🤖 LangGraph Resume Analysis Agent Processing...")
        print("=" * 50)
        
        # Analyze the resume using LangGraph workflow
        analysis_result = analyzer.analyze_resume(resume_data, job_description_data)
        
        print("\n" + "=" * 50)
        print("📊 Resume Analysis Results")
        print("=" * 50)
        
        # Display overall score
        print(f"\n🎯 OVERALL SCORE: {analysis_result['overall_score']}/100")
        
        # Display key metrics
        print(f"\n📈 KEY METRICS:")
        print(f"• Skills Match: {analysis_result['skills_analysis'].get('skill_match_percentage', 0)}%")
        print(f"• Experience Score: {analysis_result['experience_analysis'].get('experience_score', 0)}/100")
        print(f"• Formatting Score: {analysis_result['formatting_analysis'].get('overall_formatting_score', 0)}/100")
        
        # Display strengths and weaknesses
        print(f"\n✅ STRENGTHS:")
        for strength in analysis_result['strengths']:
            print(f"• {strength}")
        
        print(f"\n⚠️  WEAKNESSES:")
        for weakness in analysis_result['weaknesses']:
            print(f"• {weakness}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in analysis_result['recommendations']:
            print(f"• {rec}")
        
        print("\n" + "=" * 50)
        print("📄 DETAILED ANALYSIS REPORT")
        print("=" * 50)
        print(analysis_result['final_report'])
        
        # Save analysis result
        filename = f"{resume_data.candidate_name.replace(' ', '_')}_resume_analysis.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Resume Analysis Report\n")
            f.write(f"=====================\n\n")
            f.write(f"Candidate: {resume_data.candidate_name}\n")
            f.write(f"Job: {job_description_data.job_title} at {job_description_data.company_name}\n")
            f.write(f"Overall Score: {analysis_result['overall_score']}/100\n\n")
            f.write(analysis_result['final_report'])
        
        print(f"\n✅ Analysis saved to: {filename}")
        print("\n🎉 LangGraph Resume Analysis Agent completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. OpenAI API key in .env file")
        print("2. Internet connection")
        print("3. Valid API key with credits")
        print("4. LangGraph dependencies installed")

if __name__ == "__main__":
    main() 