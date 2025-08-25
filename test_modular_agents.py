"""
Test script for modular agents
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_jd_generator_agent():
    """Test the independent JD Generator Agent"""
    print("🧪 Testing JD Generator Agent...")
    
    try:
        from agents.jd_generator import JDGeneratorAgent
        
        # Initialize agent
        agent = JDGeneratorAgent()
        print("✅ JD Generator Agent initialized successfully")
        
        # Test status
        status = agent.get_agent_status()
        print(f"✅ Agent status: {status['status']}")
        
        # Test RAG stats
        rag_stats = agent.get_rag_stats()
        print(f"✅ RAG stats: {rag_stats.model_dump()}")
        
        # Test job descriptions
        job_descriptions = agent.get_available_job_descriptions()
        print(f"✅ Available job descriptions: {len(job_descriptions)}")
        
        print("✅ JD Generator Agent test passed!")
        return True
        
    except Exception as e:
        print(f"❌ JD Generator Agent test failed: {e}")
        return False

def test_root_agent_coordinator():
    """Test the Root Agent Coordinator"""
    print("🧪 Testing Root Agent Coordinator...")
    
    try:
        from agents.root_agent import RootAgentCoordinator
        
        # Initialize coordinator
        coordinator = RootAgentCoordinator()
        print("✅ Root Agent Coordinator initialized successfully")
        
        # Test system status
        status = coordinator.get_system_status()
        print(f"✅ System status: {status['status']}")
        
        # Test available agents
        agents = coordinator.get_available_agents()
        print(f"✅ Available agents: {agents}")
        
        # Test agent status
        jd_status = coordinator.get_agent_status('jd_generator')
        print(f"✅ JD Generator status: {jd_status}")
        
        print("✅ Root Agent Coordinator test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Root Agent Coordinator test failed: {e}")
        return False

def test_backward_compatibility():
    """Test backward compatibility"""
    print("🧪 Testing backward compatibility...")
    
    try:
        # Test old imports still work
        from agents.jd_generator import LangGraphJDGenerator, SimpleRAGJDGenerator
        from agents.root_agent import HRRootAgent
        
        print("✅ Backward compatibility imports work")
        
        # Test old class names
        jd_agent = LangGraphJDGenerator()
        root_agent = HRRootAgent()
        
        print("✅ Backward compatibility classes work")
        return True
        
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Modular Agent Structure")
    print("=" * 50)
    
    tests = [
        test_jd_generator_agent,
        test_root_agent_coordinator,
        test_backward_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Modular structure is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
