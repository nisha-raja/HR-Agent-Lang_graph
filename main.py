"""
HR Agent Suite - Main Application
Entry point for the HR Agent Suite using the root agent for coordination
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from agents.root_agent.hr_root_agent import HRRootAgent
from utils.config_manager import ConfigManager
from utils.file_manager import FileManager

def main():
    """Main application entry point"""
    print("🤖 HR Agent Suite - Main Application")
    print("=" * 50)
    
    try:
        # Initialize configuration
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        print(f"System: {config['system']['name']} v{config['system']['version']}")
        print(f"Description: {config['system']['description']}")
        
        # Validate configuration
        validation = config_manager.validate_config()
        if not validation['valid']:
            print("❌ Configuration validation failed:")
            for error in validation['errors']:
                print(f"  - {error}")
            return
        
        if validation['warnings']:
            print("⚠️ Configuration warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
        
        # Initialize root agent
        print("\n🚀 Initializing HR Root Agent...")
        root_agent = HRRootAgent()
        
        # Get system status
        status = root_agent.get_system_status()
        print(f"✅ System Status: {status['status']}")
        
        # Show available data
        job_descriptions = root_agent.get_available_job_descriptions()
        analysis_history = root_agent.get_analysis_history()
        
        print(f"📄 Available Job Descriptions: {len(job_descriptions)}")
        print(f"📊 Analysis History: {len(analysis_history)} results")
        
        # Show storage info
        file_manager = FileManager()
        storage_info = file_manager.get_storage_info()
        
        print("\n💾 Storage Information:")
        for category, info in storage_info.items():
            print(f"  {category}: {info['file_count']} files, {info['total_size_mb']} MB")
        
        print("\n🎉 HR Agent Suite is ready!")
        print("\nAvailable Operations:")
        print("1. Generate Job Description")
        print("2. Analyze Resume")
        print("3. View Job Descriptions")
        print("4. View Analysis History")
        print("5. System Status")
        print("6. Exit")
        
        # Simple CLI interface
        while True:
            try:
                choice = input("\nSelect operation (1-6): ").strip()
                
                if choice == '1':
                    generate_job_description_flow(root_agent)
                elif choice == '2':
                    analyze_resume_flow(root_agent)
                elif choice == '3':
                    view_job_descriptions(root_agent)
                elif choice == '4':
                    view_analysis_history(root_agent)
                elif choice == '5':
                    show_system_status(root_agent)
                elif choice == '6':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please select 1-6.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Failed to initialize HR Agent Suite: {e}")
        print("\nPlease check:")
        print("1. OpenAI API key in .env file")
        print("2. Required dependencies installed")
        print("3. Proper file permissions")

def generate_job_description_flow(root_agent):
    """Generate job description flow"""
    print("\n📝 Job Description Generation")
    print("=" * 40)
    
    # Get job details from user
    job_details = get_job_details_from_user()
    
    print("\n🔄 Generating job description...")
    result = root_agent.route_job_description_request(job_details)
    
    if result['success']:
        print("✅ Job description generated successfully!")
        print(f"📄 Saved as: {result['filename']}")
        print("\n📋 Generated Job Description:")
        print("-" * 50)
        print(result['description'])
    else:
        print(f"❌ Error: {result['message']}")

def analyze_resume_flow(root_agent):
    """Analyze resume flow"""
    print("\n📋 Resume Analysis")
    print("=" * 40)
    
    # Get resume and job description data
    resume_data, job_description_data = get_resume_analysis_input(root_agent)
    
    print("\n🔄 Analyzing resume...")
    result = root_agent.route_resume_analysis_request(resume_data, job_description_data)
    
    if result['success']:
        print("✅ Resume analysis completed!")
        print(f"📊 Analysis saved as: {result['analysis_filename']}")
        
        analysis = result['analysis_result']
        print(f"\n📈 Overall Score: {analysis['overall_score']}/100")
        print(f"💪 Strengths: {', '.join(analysis['strengths'][:3])}")
        print(f"⚠️ Weaknesses: {', '.join(analysis['weaknesses'][:3])}")
    else:
        print(f"❌ Error: {result['message']}")

def process_interview_flow(root_agent):
    """Process interview scheduling flow"""
    print("\n📧 Interview Scheduling")
    print("=" * 40)
    
    # Get candidate data from analysis history
    candidate_data = get_candidate_data_from_history(root_agent)
    
    if candidate_data:
        print("\n🔄 Processing candidate for interview...")
        result = root_agent.route_interview_scheduling_request(candidate_data)
        
        if result['success']:
            print("✅ Interview processing completed!")
            print(f"📧 {result['message']}")
        else:
            print(f"❌ Error: {result['message']}")
    else:
        print("❌ No candidate data available for processing")

def get_job_details_from_user():
    """Helper to get job details from user input"""
    job_details = {}
    job_details['job_title'] = input("Job Title: ").strip()
    job_details['company_name'] = input("Company Name: ").strip()
    job_details['experience_required'] = input("Experience Required (e.g., 5+ years): ").strip()
    job_details['employment_type'] = input("Employment Type (Full-time/Part-time/Contract): ").strip()
    job_details['salary_range'] = input("Salary Range (e.g., $80,000 - $100,000): ").strip()
    
    industry = input("Industry (press Enter for Technology): ").strip()
    job_details['industry'] = industry if industry else "Technology"
    
    location = input("Location (press Enter for Remote): ").strip()
    job_details['location'] = location if location else "Remote"
    
    department = input("Department (press Enter for General): ").strip()
    job_details['department'] = department if department else "General"
    
    return job_details

def get_resume_analysis_input(root_agent):
    """Helper to get resume and job description data for analysis"""
    # Get available job descriptions
    job_descriptions = root_agent.get_available_job_descriptions()
    
    if not job_descriptions:
        print("❌ No job descriptions available. Please generate a job description first.")
        return None, None
    
    # Select job description
    print("Available Job Descriptions:")
    for i, jd in enumerate(job_descriptions, 1):
        print(f"{i}. {jd['metadata']['job_title']} at {jd['metadata']['company_name']}")
    
    choice = input(f"\nSelect job description (1-{len(job_descriptions)}): ").strip()
    
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(job_descriptions):
        print("❌ Invalid choice.")
        return None, None
    
    selected_jd = job_descriptions[int(choice) - 1]
    
    # Get resume data
    print("\n📄 Resume Information:")
    resume_data = {}
    resume_data['candidate_name'] = input("Candidate Name: ").strip()
    resume_data['file_name'] = input("Resume File Name: ").strip()
    
    print("\nPaste resume content (press Enter twice when done):")
    resume_lines = []
    while True:
        line = input()
        if line == "" and resume_lines and resume_lines[-1] == "":
            break
        resume_lines.append(line)
    
    resume_data['content'] = "\n".join(resume_lines[:-1])
    
    # Prepare job description data
    job_description_data = {
        'content': selected_jd['content'],
        'job_title': selected_jd['metadata']['job_title'],
        'company_name': selected_jd['metadata']['company_name']
    }
    
    return resume_data, job_description_data

def get_candidate_data_from_history(root_agent):
    """Helper to get candidate data from analysis history for interview scheduling"""
    analysis_history = root_agent.get_analysis_history()
    
    if not analysis_history:
        print("❌ No analysis results available. Please analyze a resume first.")
        return None
    
    print("\nAnalysis History:")
    for i, analysis in enumerate(analysis_history, 1):
        data = analysis['data']
        metadata = data.get('metadata', {})
        print(f"{i}. {metadata.get('candidate_name', 'Unknown')}")
    
    choice = input(f"\nSelect analysis result (1-{len(analysis_history)}) to process for interview: ").strip()
    
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(analysis_history):
        print("❌ Invalid choice.")
        return None
    
    selected_analysis = analysis_history[int(choice) - 1]
    return selected_analysis['data']

def view_job_descriptions(root_agent: HRRootAgent):
    """View available job descriptions"""
    print("\n📄 Available Job Descriptions")
    print("-" * 30)
    
    job_descriptions = root_agent.get_available_job_descriptions()
    
    if not job_descriptions:
        print("No job descriptions available.")
        return
    
    for i, jd in enumerate(job_descriptions, 1):
        print(f"\n{i}. {jd['metadata']['job_title']} at {jd['metadata']['company_name']}")
        print(f"   Experience: {jd['metadata']['experience_required']}")
        print(f"   Type: {jd['metadata']['employment_type']}")
        print(f"   Salary: {jd['metadata']['salary_range']}")
        print(f"   Location: {jd['metadata']['location']}")

def view_analysis_history(root_agent: HRRootAgent):
    """View analysis history"""
    print("\n📊 Analysis History")
    print("-" * 20)
    
    analysis_history = root_agent.get_analysis_history()
    
    if not analysis_history:
        print("No analysis results available.")
        return
    
    for i, analysis in enumerate(analysis_history, 1):
        data = analysis['data']
        metadata = data.get('metadata', {})
        print(f"\n{i}. {metadata.get('candidate_name', 'Unknown')}")
        print(f"   Score: {data.get('overall_score', 0)}/100")
        print(f"   Date: {metadata.get('created_at', 'Unknown')}")

def show_system_status(root_agent: HRRootAgent):
    """Show system status"""
    print("\n🔧 System Status")
    print("-" * 15)
    
    status = root_agent.get_system_status()
    
    print(f"Status: {status['status']}")
    print("\nAgents:")
    for agent, state in status['agents'].items():
        print(f"  {agent}: {state}")
    
    print("\nDirectories:")
    for name, path in status['directories'].items():
        print(f"  {name}: {path}")

if __name__ == "__main__":
    main()
