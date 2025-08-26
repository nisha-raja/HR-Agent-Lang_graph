# PHOENKAI AI - HR Agent Suite

A comprehensive HR management system with AI-powered agents for job description generation, resume analysis, and interview scheduling.

## 🏗️ Project Structure

```
hr-agent/
├── agents/                          # AI Agent Modules
│   ├── jd_generator/               # Job Description Generator Agent
│   │   ├── agent.py                # Main agent logic
│   │   ├── api.py                  # FastAPI endpoints
│   │   ├── config.py               # Configuration
│   │   ├── models.py               # Pydantic models
│   │   ├── utils.py                # Utility functions
│   │   └── __init__.py
│   ├── resume_analyzer/            # Resume Analysis Agent
│   │   ├── agent.py                # Main agent logic with LangGraph
│   │   ├── api.py                  # FastAPI endpoints
│   │   ├── config.py               # Configuration
│   │   ├── models.py               # Pydantic models
│   │   ├── utils.py                # Utility functions
│   │   └── __init__.py
│   ├── interview_scheduler/        # Interview Scheduling Agent
│   │   ├── agent.py                # Main agent logic
│   │   ├── api.py                  # FastAPI endpoints
│   │   ├── config.py               # Configuration
│   │   ├── models.py               # Pydantic models
│   │   ├── utils.py                # Utility functions
│   │   └── __init__.py
│   └── root_agent/                 # Root Agent Coordinator
│       ├── coordinator.py          # Main coordinator logic
│       ├── api.py                  # FastAPI gateway
│       └── __init__.py
├── frontend/                       # React/Next.js Frontend
│   ├── src/
│   │   ├── app/                    # Next.js app router
│   │   │   ├── page.tsx            # Dashboard
│   │   │   ├── people/             # People management
│   │   │   │   ├── page.tsx        # Overview
│   │   │   │   ├── jd/             # Job Description Generator
│   │   │   │   ├── resume/         # Resume Analyzer
│   │   │   │   └── interview/      # Interview Scheduler
│   │   │   └── layout.tsx          # Root layout
│   │   ├── components/             # React components
│   │   │   └── Layout/             # Layout components
│   │   └── services/               # API services
│   │       └── api.ts              # API client
│   ├── package.json
│   └── README.md
├── data/                           # Data storage
│   ├── job_descriptions/           # Generated job descriptions
│   ├── resumes/                    # Uploaded resumes
│   ├── analysis_results/           # Resume analysis results
│   ├── email_templates/            # Email templates
│   └── scheduling/                 # Interview schedules
├── requirements.txt                # Python dependencies
├── start_services.py               # Service startup script
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

## 🚀 How It Works

### Architecture Overview

The system follows a **microservices architecture** with independent, plug-and-play AI agents:

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   React Frontend │ ◄─────────────► │  Root Agent     │
│   (Port 3000)    │                 │  Gateway        │
└─────────────────┘                 │  (Port 8000)    │
                                    └─────────────────┘
                                           │
                                           │ Internal Calls
                                           ▼
                    ┌─────────────────────────────────────────┐
                    │                                         │
            ┌───────▼────────┐    ┌────────▼────────┐    ┌────▼────────┐
            │ JD Generator    │    │ Resume Analyzer │    │ Interview   │
            │ Agent           │    │ Agent           │    │ Scheduler   │
            │ (Port 8001)     │    │ (Port 8002)     │    │ Agent       │
            │                 │    │                 │    │ (Port 8003) │
            └─────────────────┘    └─────────────────┘    └─────────────┘
```

### Agent Communication Flow

1. **Frontend** → **Root Agent Gateway** (Port 8000)
   - All requests go through the Root Agent first
   - Gateway routes requests to appropriate sub-agents

2. **Root Agent** → **Sub-Agents** (Ports 8001, 8002, 8003)
   - Internal method calls to sub-agents
   - Each agent is independently deployable

3. **Data Flow**:
   - Frontend sends data in standardized format
   - Root Agent transforms data for sub-agents
   - Sub-agents process and return results
   - Results are transformed back to frontend format

### Key Components

#### 1. **JD Generator Agent** (Port 8001)
- **Purpose**: Generate comprehensive job descriptions using AI
- **Input**: Job requirements (title, company, experience, salary, etc.)
- **Output**: Detailed job description with responsibilities, requirements, benefits
- **Technology**: LangChain + OpenAI GPT

#### 2. **Resume Analyzer Agent** (Port 8002)
- **Purpose**: Analyze resumes against job descriptions
- **Input**: Resume file + Job description
- **Output**: Analysis score, strengths, weaknesses, recommendations
- **Technology**: LangGraph workflow + OpenAI GPT

#### 3. **Interview Scheduler Agent** (Port 8003)
- **Purpose**: Schedule interviews and send automated emails
- **Input**: Candidate data + Interview details
- **Output**: Scheduled interviews with email confirmations
- **Technology**: SMTP + Calendar integration

#### 4. **Root Agent Coordinator** (Port 8000)
- **Purpose**: Central gateway and request router
- **Functions**:
  - Route requests to appropriate agents
  - Transform data between frontend and agent formats
  - Provide unified API interface
  - Handle error responses

## 🛠️ Technology Stack

### Backend
- **Python 3.9+**
- **FastAPI** - REST API framework
- **LangChain** - AI/LLM framework
- **LangGraph** - Workflow orchestration
- **OpenAI GPT** - AI model
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Chakra UI** - Component library
- **Axios** - HTTP client
- **React Hook Form** - Form management

### Data Storage
- **File-based storage** (JSON, TXT)
- **Structured data directories**
- **Email templates** (HTML)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API key

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd hr-agent

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start Services
```bash
# Start all services (recommended)
python start_services.py

# Or start individually:
# Terminal 1: Root Agent
python -m uvicorn agents.root_agent.api:app --host 0.0.0.0 --port 8000

# Terminal 2: JD Generator
python -m uvicorn agents.jd_generator.api:app --host 0.0.0.0 --port 8001

# Terminal 3: Resume Analyzer
python -m uvicorn agents.resume_analyzer.api:app --host 0.0.0.0 --port 8002

# Terminal 4: Interview Scheduler
python -m uvicorn agents.interview_scheduler.api:app --host 0.0.0.0 --port 8003

# Terminal 5: Frontend
cd frontend && npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Root Agent API**: http://localhost:8000
- **JD Generator API**: http://localhost:8001
- **Resume Analyzer API**: http://localhost:8002
- **Interview Scheduler API**: http://localhost:8003

## 📋 API Endpoints

### Root Agent Gateway (Port 8000)
```
GET    /health                    # System health check
GET    /agents                    # List all agents
GET    /jd/list                   # List job descriptions
POST   /jd/generate               # Generate job description
POST   /jd/save                   # Save job description
POST   /resume/analyze            # Analyze resume
GET    /resume/history            # Get analysis history
POST   /interview/schedule        # Schedule interview
GET    /interview/templates       # Get email templates
POST   /ai/assist                 # AI assistant routing
```

### JD Generator Agent (Port 8001)
```
GET    /health                    # Health check
POST   /generate                  # Generate JD
POST   /save                      # Save JD
GET    /list                      # List JDs
```

### Resume Analyzer Agent (Port 8002)
```
GET    /health                    # Health check
POST   /analyze                   # Analyze resume
GET    /history                   # Analysis history
```

### Interview Scheduler Agent (Port 8003)
```
GET    /health                    # Health check
POST   /schedule                  # Schedule interview
GET    /templates                 # Email templates
GET    /slots                     # Available slots
```

## 🔧 Configuration

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Agent Configuration
JD_GENERATOR_PORT=8001
RESUME_ANALYZER_PORT=8002
INTERVIEW_SCHEDULER_PORT=8003
ROOT_AGENT_PORT=8000

# SMTP Configuration (for email sending)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Data Directories
The system uses file-based storage in the `data/` directory:
- `data/job_descriptions/` - Generated job descriptions
- `data/resumes/` - Uploaded resume files
- `data/analysis_results/` - Resume analysis results
- `data/email_templates/` - Email templates
- `data/scheduling/` - Interview schedules

## 🎯 Features

### Job Description Generator
- ✅ AI-powered job description creation
- ✅ Customizable job requirements
- ✅ Industry-specific templates
- ✅ Export to multiple formats

### Resume Analyzer
- ✅ AI-powered resume analysis
- ✅ Skills matching against job descriptions
- ✅ Experience relevance scoring
- ✅ Detailed feedback and recommendations
- ✅ Analysis history tracking

### Interview Scheduler
- ✅ Automated interview scheduling
- ✅ Email notifications
- ✅ Calendar integration
- ✅ Template management
- ✅ Candidate tracking

### Frontend Features
- ✅ Modern, responsive UI
- ✅ Real-time updates
- ✅ File upload support
- ✅ Progress indicators
- ✅ Error handling
- ✅ Mobile-friendly design

## 🔒 Security & Best Practices

### Security Features
- CORS middleware enabled
- Input validation with Pydantic
- Error handling and logging
- Environment variable configuration
- File upload restrictions

### Code Quality
- Type hints throughout
- Modular architecture
- Separation of concerns
- Comprehensive error handling
- Clean code principles

## 🚀 Deployment

### Development
```bash
python start_services.py
```

### Production
```bash
# Use process managers like PM2 or systemd
# Configure reverse proxy (nginx)
# Set up SSL certificates
# Use environment-specific configurations
```

### Docker (Future Enhancement)
```dockerfile
# Dockerfile example for production
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "start_services.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints

## 🔄 Version History

- **v1.0.0** - Initial release with modular agent architecture
- **v1.1.0** - Added React frontend with Chakra UI
- **v1.2.0** - Enhanced resume analysis with LangGraph workflows
- **v1.3.0** - Improved error handling and API stability

---

**PHOENKAI AI - HR Agent Suite** - Empowering HR professionals with AI-driven automation. 