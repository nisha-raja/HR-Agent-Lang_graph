# 🏗️ Modular Agent Architecture

## Overview

The HR Agent Suite has been restructured into a fully modular, plug-and-play architecture where each agent is completely independent and deployable separately. This makes it easy to:

- **Deploy individual agents** without the full suite
- **Integrate with any UI** (React, Vue, Angular, etc.)
- **Scale agents independently**
- **Maintain clean separation of concerns**

## 🏛️ Architecture Structure

```
agents/
├── root_agent/                    # Pure Coordinator
│   ├── __init__.py
│   ├── coordinator.py            # Lightweight coordinator
│   └── api.py                    # Coordination API (future)
├── jd_generator/                 # Independent JD Generator
│   ├── __init__.py
│   ├── agent.py                  # Pure JD generation logic
│   ├── api.py                    # REST API endpoints
│   ├── config.py                 # Agent-specific config
│   ├── models.py                 # Data models
│   └── utils.py                  # Agent-specific utilities
├── resume_analyzer/              # Independent Resume Analyzer
│   ├── __init__.py
│   ├── agent.py                  # Pure resume analysis logic
│   ├── api.py                    # REST API endpoints
│   ├── config.py                 # Agent-specific config
│   ├── models.py                 # Data models
│   └── utils.py                  # Agent-specific utilities
└── interview_scheduler/          # Independent Interview Scheduler
    ├── __init__.py
    ├── agent.py                  # Pure scheduling logic
    ├── api.py                    # REST API endpoints
    ├── config.py                 # Agent-specific config
    ├── models.py                 # Data models
    └── utils.py                  # Agent-specific utilities
```

## 🔧 Key Principles

### 1. **Complete Independence**
- Each agent has its own configuration, file management, and utilities
- No cross-dependencies between agents
- Each agent can be deployed and run independently

### 2. **Clean API Interfaces**
- Standardized request/response formats
- RESTful API endpoints for each agent
- Easy integration with any frontend framework

### 3. **Plug-and-Play Design**
- Deploy only the agents you need
- Easy to add new agents
- Backward compatibility maintained

### 4. **Root Agent as Pure Coordinator**
- No business logic in root agent
- Only routes requests to appropriate agents
- Lightweight and fast

## 🚀 Deployment Options

### Option 1: Full Suite Deployment
```bash
# Deploy all agents together
python main.py
```

### Option 2: Individual Agent Deployment
```bash
# Deploy only JD Generator
python -m agents.jd_generator.api

# Deploy only Resume Analyzer
python -m agents.resume_analyzer.api

# Deploy only Interview Scheduler
python -m agents.interview_scheduler.api
```

### Option 3: Microservices Architecture
```bash
# JD Generator on port 8001
uvicorn agents.jd_generator.api:app --host 0.0.0.0 --port 8001

# Resume Analyzer on port 8002
uvicorn agents.resume_analyzer.api:app --host 0.0.0.0 --port 8002

# Interview Scheduler on port 8003
uvicorn agents.interview_scheduler.api:app --host 0.0.0.0 --port 8003
```

## 🔌 Integration Examples

### React Integration
```javascript
// JD Generator API calls
const generateJD = async (jobDetails) => {
  const response = await fetch('http://localhost:8001/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_details: jobDetails })
  });
  return response.json();
};

// Resume Analyzer API calls
const analyzeResume = async (resumeData, jobDescriptionData) => {
  const response = await fetch('http://localhost:8002/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      resume_data: resumeData, 
      job_description_data: jobDescriptionData 
    })
  });
  return response.json();
};
```

### Python Integration
```python
from agents.jd_generator import JDGeneratorAgent
from agents.resume_analyzer import LangGraphResumeAnalyzer

# Use only JD Generator
jd_agent = JDGeneratorAgent()
result = jd_agent.generate_job_description_from_dict(job_details)

# Use only Resume Analyzer
resume_agent = LangGraphResumeAnalyzer()
result = resume_agent.analyze_resume(resume_data, job_description_data)
```

## 📋 API Endpoints

### JD Generator Agent (Port 8001)
- `GET /` - Health check
- `GET /health` - Agent health
- `POST /generate` - Generate job description
- `POST /save` - Save job description
- `GET /job-descriptions` - List all job descriptions
- `DELETE /job-descriptions/{filename}` - Delete job description
- `GET /rag-stats` - RAG system statistics
- `GET /config` - Agent configuration
- `GET /status` - Comprehensive status

### Resume Analyzer Agent (Port 8002)
- `GET /` - Health check
- `POST /analyze` - Analyze resume
- `GET /analysis-history` - Get analysis history
- `GET /status` - Agent status

### Interview Scheduler Agent (Port 8003)
- `GET /` - Health check
- `POST /schedule` - Schedule interview
- `GET /templates` - Get email templates
- `GET /status` - Agent status

## 🔄 Migration Guide

### From Old Structure
The new structure maintains backward compatibility:

```python
# Old way (still works)
from agents.jd_generator import LangGraphJDGenerator
from agents.root_agent import HRRootAgent

# New way (recommended)
from agents.jd_generator import JDGeneratorAgent
from agents.root_agent import RootAgentCoordinator
```

### Configuration Changes
Each agent now has its own configuration:

```python
# JD Generator config
from agents.jd_generator.config import JDGeneratorConfig
config = JDGeneratorConfig()

# Resume Analyzer config
from agents.resume_analyzer.config import ResumeAnalyzerConfig
config = ResumeAnalyzerConfig()
```

## 🧪 Testing

Run the modular architecture tests:

```bash
python test_modular_agents.py
```

This tests:
- ✅ JD Generator Agent independence
- ✅ Root Agent Coordinator functionality
- ✅ Backward compatibility
- ✅ Agent status and health checks

## 🎯 Benefits

1. **Scalability**: Deploy agents independently based on load
2. **Maintainability**: Clean separation of concerns
3. **Flexibility**: Use only the agents you need
4. **Integration**: Easy to integrate with any UI framework
5. **Deployment**: Multiple deployment options (monolith, microservices)
6. **Testing**: Independent testing of each agent
7. **Development**: Work on agents independently

## 🔮 Future Enhancements

1. **Docker Containers**: Each agent in its own container
2. **Kubernetes Deployment**: Orchestrate agents independently
3. **Load Balancing**: Distribute load across agent instances
4. **Monitoring**: Independent monitoring for each agent
5. **Caching**: Agent-specific caching strategies
6. **Database**: Independent databases for each agent
