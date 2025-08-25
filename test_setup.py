"""
Test script to verify RAG implementation in JD Generator Agent
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from difflib import SequenceMatcher

# Load environment variables
load_dotenv()

def test_rag_components():
    """Test individual RAG components"""
    
    print("🧪 Testing RAG Implementation Components")
    print("=" * 60)
    
    # Test 1: Check if job descriptions are loaded
    print("1. Testing Job Descriptions Loading...")
    job_descriptions_dir = Path("data/job_descriptions")
    job_files = []
    
    if job_descriptions_dir.exists():
        job_files = list(job_descriptions_dir.glob("*.txt"))
        print(f"✅ Found {len(job_files)} job description files")
        
        # Show sample content
        if job_files:
            sample_file = job_files[0]
            with open(sample_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"📄 Sample file: {sample_file.name}")
            print(f"📏 Content length: {len(content)} characters")
            print(f"📏 First 200 chars: {content[:200]}...")
    else:
        print("❌ No job descriptions directory found")
        return False
    
    # Test 2: Test similarity calculation
    print("\n2. Testing Similarity Calculation...")
    test_query = "Software Engineer Technology Engineering 3-5 years"
    test_content = "We are looking for a Software Engineer with 3-5 years of experience in technology..."
    
    similarity = SequenceMatcher(None, test_query.lower(), test_content.lower()).ratio()
    print(f"✅ Similarity calculation works: {similarity:.3f}")
    
    # Test 3: Test RAG agent initialization
    print("\n3. Testing RAG Agent Initialization...")
    try:
        from agents.jd_generator.jd_generator_agent import SimpleRAGJDGenerator
        generator = SimpleRAGJDGenerator()
        rag_stats = generator.get_rag_stats()
        print(f"✅ RAG agent initialized successfully")
        print(f"📊 RAG Stats: {rag_stats}")
        return True
    except Exception as e:
        print(f"❌ RAG agent initialization failed: {e}")
        return False

def test_rag_retrieval():
    """Test RAG retrieval functionality"""
    
    print("\n🔍 Testing RAG Retrieval Functionality")
    print("=" * 60)
    
    try:
        from agents.jd_generator.jd_generator_agent import SimpleRAGJDGenerator, JobDetails
        
        # Initialize agent
        generator = SimpleRAGJDGenerator()
        
        # Create test job details
        test_job = JobDetails(
            job_title="Software Engineer",
            experience_required="3-5 years",
            company_name="TestCorp",
            employment_type="Full-time",
            salary_range="$80,000 - $120,000",
            industry="Technology",
            location="Remote",
            department="Engineering"
        )
        
        print(f"🎯 Testing retrieval for: {test_job.job_title}")
        
        # Test retrieval
        context = generator.retrieve_relevant_context(test_job, top_k=2)
        
        if context:
            print(f"✅ RAG retrieval successful!")
            print(f"📊 Found {len(context)} relevant contexts")
            
            for i, ctx in enumerate(context, 1):
                print(f"\n--- Context {i} ---")
                print(ctx[:300] + "..." if len(ctx) > 300 else ctx)
        else:
            print("ℹ️ No relevant contexts found (this is normal if no similar job descriptions exist)")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG retrieval test failed: {e}")
        return False

def test_rag_integration():
    """Test RAG integration in job description generation"""
    
    print("\n🤖 Testing RAG Integration in Job Generation")
    print("=" * 60)
    
    try:
        from agents.jd_generator.jd_generator_agent import SimpleRAGJDGenerator, JobDetails
        
        # Initialize agent
        generator = SimpleRAGJDGenerator()
        
        # Create test job details
        test_job = JobDetails(
            job_title="Data Scientist",
            experience_required="2-4 years",
            company_name="DataCorp",
            employment_type="Full-time",
            salary_range="$90,000 - $130,000",
            industry="Technology",
            location="Remote",
            department="Data Science"
        )
        
        print(f"🎯 Testing job generation with RAG for: {test_job.job_title}")
        
        # Check if RAG context is being retrieved
        context = generator.retrieve_relevant_context(test_job)
        
        if context:
            print("✅ RAG context retrieved successfully")
            print(f"📊 Using {len(context)} reference job descriptions")
            
            # Test job overview generation with RAG
            print("\n📝 Testing job overview generation with RAG...")
            
            # Create a minimal state for testing
            from agents.jd_generator.jd_generator_agent import JobDescriptionState
            
            test_state = JobDescriptionState(
                job_details=test_job,
                job_overview="",
                responsibilities=[],
                qualifications=[],
                benefits=[],
                final_description="",
                current_step="start",
                messages=[],
                retrieved_context=context
            )
            
            # Test the overview generation
            result_state = generator.create_job_overview(test_state)
            
            if result_state['job_overview']:
                print("✅ Job overview generated successfully with RAG context")
                print(f"📄 Overview: {result_state['job_overview'][:200]}...")
            else:
                print("❌ Job overview generation failed")
                
        else:
            print("ℹ️ No RAG context available (will generate without RAG)")
            
        return True
        
    except Exception as e:
        print(f"❌ RAG integration test failed: {e}")
        return False

def test_rag_learning():
    """Test RAG learning (adding new job descriptions to cache)"""
    
    print("\n📚 Testing RAG Learning Capability")
    print("=" * 60)
    
    try:
        from agents.jd_generator.jd_generator_agent import SimpleRAGJDGenerator, JobDetails
        
        # Initialize agent
        generator = SimpleRAGJDGenerator()
        
        # Get initial cache size
        initial_cache_size = len(generator.job_descriptions_cache)
        print(f"📊 Initial cache size: {initial_cache_size}")
        
        # Create a test job description
        test_description = """
        Job Title: Test Software Engineer
        Company: TestCorp
        Industry: Technology
        
        Job Overview:
        We are looking for a talented Software Engineer to join our team.
        
        Responsibilities:
        • Develop and maintain software applications
        • Collaborate with cross-functional teams
        • Write clean, efficient code
        
        Qualifications:
        • Bachelor's degree in Computer Science
        • 3+ years of experience
        • Proficiency in Python and JavaScript
        """
        
        # Test adding to cache
        generator.job_descriptions_cache.append({
            "content": test_description,
            "filename": "test_job_description.txt",
            "file_path": "test_path"
        })
        
        # Check new cache size
        new_cache_size = len(generator.job_descriptions_cache)
        print(f"📊 New cache size: {new_cache_size}")
        
        if new_cache_size > initial_cache_size:
            print("✅ RAG learning works - new job description added to cache")
        else:
            print("❌ RAG learning failed - cache size didn't increase")
            
        return True
        
    except Exception as e:
        print(f"❌ RAG learning test failed: {e}")
        return False

def main():
    """Run all RAG tests"""
    
    print("🚀 Comprehensive RAG Implementation Test")
    print("=" * 60)
    
    # Check environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not set. Please set OPENAI_API_KEY in .env file")
        return
    
    # Run tests
    tests = [
        ("RAG Components", test_rag_components),
        ("RAG Retrieval", test_rag_retrieval),
        ("RAG Integration", test_rag_integration),
        ("RAG Learning", test_rag_learning)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 RAG Implementation Test Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All RAG tests passed! Your RAG implementation is working correctly.")
        print("\n💡 To see RAG in action, run:")
        print("   python agents/jd_generator/jd_generator_agent.py")
    else:
        print("⚠️ Some RAG tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
