#!/usr/bin/env python3
"""
Start all HR Agent services and React frontend
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def run_command(command, cwd=None, background=False):
    """Run a command and return the process"""
    print(f"Running: {command}")
    if background:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    else:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        return result

def check_port(port):
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def main():
    print("🚀 Starting HR Agent Suite...")
    
    # Check if we're in the right directory
    if not Path("agents").exists():
        print("❌ Error: Please run this script from the hr-agent root directory")
        sys.exit(1)
    
    processes = []
    
    try:
        # Start Root Agent (Port 8000)
        print("\n📡 Starting Root Agent Gateway (Port 8000)...")
        if not check_port(8000):
            root_process = run_command(
                "python -m agents.root_agent.api",
                background=True
            )
            processes.append(("Root Agent", root_process))
            time.sleep(2)
        else:
            print("⚠️  Port 8000 already in use, skipping Root Agent")
        
        # Start JD Generator (Port 8001)
        print("\n📝 Starting JD Generator Agent (Port 8001)...")
        if not check_port(8001):
            jd_process = run_command(
                "python -m agents.jd_generator.api",
                background=True
            )
            processes.append(("JD Generator", jd_process))
            time.sleep(2)
        else:
            print("⚠️  Port 8001 already in use, skipping JD Generator")
        
        # Start Resume Analyzer (Port 8002)
        print("\n📊 Starting Resume Analyzer Agent (Port 8002)...")
        if not check_port(8002):
            resume_process = run_command(
                "python -m agents.resume_analyzer.api",
                background=True
            )
            processes.append(("Resume Analyzer", resume_process))
            time.sleep(2)
        else:
            print("⚠️  Port 8002 already in use, skipping Resume Analyzer")
        
        # Start Interview Scheduler (Port 8003)
        print("\n📅 Starting Interview Scheduler Agent (Port 8003)...")
        if not check_port(8003):
            interview_process = run_command(
                "python -m agents.interview_scheduler.api",
                background=True
            )
            processes.append(("Interview Scheduler", interview_process))
            time.sleep(2)
        else:
            print("⚠️  Port 8003 already in use, skipping Interview Scheduler")
        
        # Start React Frontend (Port 3000)
        print("\n🌐 Starting React Frontend (Port 3000)...")
        if not check_port(3000):
            frontend_process = run_command(
                "npm run dev",
                cwd="frontend",
                background=True
            )
            processes.append(("React Frontend", frontend_process))
            time.sleep(5)
        else:
            print("⚠️  Port 3000 already in use, skipping React Frontend")
        
        print("\n✅ All services started successfully!")
        print("\n📋 Service URLs:")
        print("   • Root Agent Gateway: http://localhost:8000")
        print("   • JD Generator API: http://localhost:8001")
        print("   • Resume Analyzer API: http://localhost:8002")
        print("   • Interview Scheduler API: http://localhost:8003")
        print("   • React Frontend: http://localhost:3000")
        print("\n🎯 Open http://localhost:3000 in your browser to access the UI")
        print("\n⏹️  Press Ctrl+C to stop all services")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping all services...")
        
        for name, process in processes:
            try:
                print(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"Error stopping {name}: {e}")
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
