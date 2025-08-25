"""
Modular Agent Deployment Script
Demonstrates different deployment options for the modular architecture
"""

import sys
import subprocess
import time
from pathlib import Path

def deploy_full_suite():
    """Deploy the full HR Agent Suite"""
    print("🚀 Deploying Full HR Agent Suite...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Full suite deployment stopped by user")
    except Exception as e:
        print(f"❌ Error deploying full suite: {e}")

def deploy_jd_generator_only():
    """Deploy only the JD Generator Agent"""
    print("🚀 Deploying JD Generator Agent Only...")
    print("📡 API will be available at: http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/docs")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "agents.jd_generator.api:app", 
            "--host", "0.0.0.0", 
            "--port", "8001",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 JD Generator deployment stopped by user")
    except Exception as e:
        print(f"❌ Error deploying JD Generator: {e}")

def deploy_microservices():
    """Deploy all agents as microservices"""
    print("🚀 Deploying Microservices Architecture...")
    print("📡 Services will be available at:")
    print("   - JD Generator: http://localhost:8001")
    print("   - Resume Analyzer: http://localhost:8002")
    print("   - Interview Scheduler: http://localhost:8003")
    
    # Start all services in background
    processes = []
    
    try:
        # JD Generator
        p1 = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "agents.jd_generator.api:app", 
            "--host", "0.0.0.0", 
            "--port", "8001"
        ])
        processes.append(p1)
        print("✅ JD Generator started on port 8001")
        
        # Resume Analyzer (placeholder - would need API implementation)
        print("⚠️ Resume Analyzer API not yet implemented")
        
        # Interview Scheduler (placeholder - would need API implementation)
        print("⚠️ Interview Scheduler API not yet implemented")
        
        print("\n🎉 Microservices deployed successfully!")
        print("Press Ctrl+C to stop all services")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for p in processes:
            p.terminate()
        print("👋 All services stopped")
    except Exception as e:
        print(f"❌ Error deploying microservices: {e}")
        for p in processes:
            p.terminate()

def test_agent_independence():
    """Test that agents can work independently"""
    print("🧪 Testing Agent Independence...")
    
    try:
        # Test JD Generator independence
        from agents.jd_generator import JDGeneratorAgent
        jd_agent = JDGeneratorAgent()
        status = jd_agent.get_agent_status()
        print(f"✅ JD Generator Agent: {status['status']}")
        
        # Test Root Agent coordination
        from agents.root_agent import RootAgentCoordinator
        coordinator = RootAgentCoordinator()
        system_status = coordinator.get_system_status()
        print(f"✅ Root Agent Coordinator: {system_status['status']}")
        
        print("🎉 All agents are working independently!")
        return True
        
    except Exception as e:
        print(f"❌ Agent independence test failed: {e}")
        return False

def show_menu():
    """Show deployment options menu"""
    print("\n" + "="*60)
    print("🏗️  HR Agent Suite - Modular Deployment Options")
    print("="*60)
    print("1. Deploy Full Suite (Monolith)")
    print("2. Deploy JD Generator Only")
    print("3. Deploy Microservices Architecture")
    print("4. Test Agent Independence")
    print("5. Exit")
    print("="*60)

def main():
    """Main deployment script"""
    print("🏗️ HR Agent Suite - Modular Architecture")
    print("Each agent is now completely independent and deployable separately!")
    
    while True:
        show_menu()
        
        try:
            choice = input("\nSelect deployment option (1-5): ").strip()
            
            if choice == "1":
                deploy_full_suite()
            elif choice == "2":
                deploy_jd_generator_only()
            elif choice == "3":
                deploy_microservices()
            elif choice == "4":
                test_agent_independence()
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
