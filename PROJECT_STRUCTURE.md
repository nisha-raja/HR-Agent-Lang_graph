# Project Structure & Architecture Documentation

## 📁 Complete Project Structure

```
hr-agent/
├── 📁 agents/                          # AI Agent Modules (Microservices)
│   ├── 📁 jd_generator/               # Job Description Generator Agent
│   │   ├── agent.py                   # Main agent logic with LangChain
│   │   ├── api.py                     # FastAPI endpoints (Port 8001)
│   │   ├── config.py                  # Configuration management
│   │   ├── models.py                  # Pydantic data models
│   │   ├── utils.py                   # Utility functions
│   │   └── __init__.py                # Module exports
│   ├── 📁 resume_analyzer/            # Resume Analysis Agent
│   │   ├── agent.py                   # Main agent logic with LangGraph
│   │   ├── api.py                     # FastAPI endpoints (Port 8002)
│   │   ├── config.py                  # Configuration management
│   │   ├── models.py                  # Pydantic data models
│   │   ├── utils.py                   # Utility functions
│   │   └── __init__.py                # Module exports
│   ├── 📁 interview_scheduler/        # Interview Scheduling Agent
│   │   ├── agent.py                   # Main agent logic
│   │   ├── api.py                     # FastAPI endpoints (Port 8003)
│   │   ├── config.py                  # Configuration management
│   │   ├── models.py                  # Pydantic data models
│   │   ├── utils.py                   # Utility functions
│   │   └── __init__.py                # Module exports
│   └── 📁 root_agent/                 # Root Agent Coordinator
│       ├── coordinator.py             # Main coordinator logic
│       ├── api.py                     # FastAPI gateway (Port 8000)
│       └── __init__.py                # Module exports
├── 📁 frontend/                       # React/Next.js Frontend
│   ├── 📁 src/
│   │   ├── 📁 app/                    # Next.js app router
│   │   │   ├── page.tsx               # Dashboard page
│   │   │   ├── layout.tsx             # Root layout
│   │   │   ├── providers.tsx          # Chakra UI providers
│   │   │   └── 📁 people/             # People management section
│   │   │       ├── page.tsx           # People overview
│   │   │       ├── 📁 jd/             # Job Description Generator
│   │   │       │   └── page.tsx       # JD creation page
│   │   │       ├── 📁 resume/         # Resume Analyzer
│   │   │       │   └── page.tsx       # Resume analysis page
│   │   │       └── 📁 interview/      # Interview Scheduler
│   │   │           └── page.tsx       # Interview scheduling page
│   │   ├── 📁 components/             # React components
│   │   │   └── 📁 Layout/             # Layout components
│   │   │       ├── Sidebar.tsx        # Navigation sidebar
│   │   │       ├── Header.tsx         # Top header
│   │   │       ├── AIChatBar.tsx      # AI chat interface
│   │   │       └── MainLayout.tsx     # Main layout wrapper
│   │   └── 📁 services/               # API services
│   │       └── api.ts                 # API client with Axios
│   ├── package.json                   # Node.js dependencies
│   ├── next.config.js                 # Next.js configuration
│   ├── tailwind.config.js             # Tailwind CSS configuration
│   └── README.md                      # Frontend documentation
├── 📁 data/                           # Data storage (File-based)
│   ├── 📁 job_descriptions/           # Generated job descriptions
│   ├── 📁 resumes/                    # Uploaded resume files
│   ├── 📁 analysis_results/           # Resume analysis results
│   ├── 📁 email_templates/            # Email templates
│   └── 📁 scheduling/                 # Interview schedules
├── 📁 docs/                           # Documentation
│   └── INTERVIEW_SCHEDULER.md         # Interview scheduler docs
├── requirements.txt                   # Python dependencies
├── start_services.py                  # Service startup script
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── README.md                          # Main project documentation
└── PROJECT_STRUCTURE.md               # This file
```

## 🔄 Data Flow Architecture

### 1. **Frontend → Backend Communication**

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   React Frontend │ ◄─────────────► │  Root Agent     │
│   (Port 3000)    │                 │  Gateway        │
│                  │                 │  (Port 8000)    │
│  - Dashboard     │                 │                 │
│  - JD Generator  │                 │                 │
│  - Resume Analyzer│                 │                 │
│  - Interview     │                 │                 │
└─────────────────┘                 └─────────────────┘
```

### 2. **Root Agent → Sub-Agents Communication**

```
┌─────────────────┐
│  Root Agent     │
│  Gateway        │
│  (Port 8000)    │
└─────────┬───────┘
          │
          ├───► JD Generator (Port 8001)
          ├───► Resume Analyzer (Port 8002)
          └───► Interview Scheduler (Port 8003)
```

### 3. **Agent Internal Architecture**

Each agent follows this internal structure:

```
┌─────────────────┐
│   FastAPI       │  ← HTTP endpoints
│   (api.py)      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Agent Logic   │  ← Main business logic
│   (agent.py)    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Utilities     │  ← Helper functions
│   (utils.py)    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Data Models   │  ← Pydantic models
│   (models.py)   │
└─────────────────┘
```

## 🧩 Component Breakdown

### 1. **Frontend Components**

#### **Layout Components** (`frontend/src/components/Layout/`)
- **`Sidebar.tsx`**: Navigation sidebar with agent links
- **`Header.tsx`**: Top header with user info and notifications
- **`AIChatBar.tsx`**: AI chat interface for dynamic routing
- **`MainLayout.tsx`**: Main layout wrapper combining all components

#### **Page Components** (`frontend/src/app/`)
- **`page.tsx`**: Dashboard with system overview
- **`people/page.tsx`**: People management overview
- **`people/jd/page.tsx`**: Job description generator interface
- **`people/resume/page.tsx`**: Resume analyzer interface
- **`people/interview/page.tsx`**: Interview scheduler interface

#### **Services** (`frontend/src/services/`)
- **`api.ts`**: Centralized API client with Axios
  - Root agent service calls
  - Individual agent service calls
  - Data transformation utilities
  - Error handling

### 2. **Backend Agents**

#### **Root Agent** (`agents/root_agent/`)
- **`coordinator.py`**: Main coordination logic
  - Routes requests to appropriate agents
  - Transforms data between frontend and agent formats
  - Handles error responses
  - Provides system status

- **`api.py`**: FastAPI gateway
  - Central entry point for all requests
  - CORS middleware
  - Request routing
  - Response formatting

#### **JD Generator Agent** (`agents/jd_generator/`)
- **`agent.py`**: Main JD generation logic
  - LangChain integration
  - OpenAI GPT prompts
  - Job description formatting
  - Quality validation

- **`api.py`**: JD-specific endpoints
  - `/generate`: Create new job descriptions
  - `/save`: Save generated descriptions
  - `/list`: Retrieve saved descriptions

- **`models.py`**: Data models
  - `JobDetails`: Input job requirements
  - `JobDescription`: Generated job description
  - `JobDescriptionResponse`: API response format

#### **Resume Analyzer Agent** (`agents/resume_analyzer/`)
- **`agent.py`**: Main analysis logic with LangGraph
  - Skills analysis workflow
  - Experience analysis workflow
  - Formatting analysis workflow
  - Overall scoring calculation

- **`api.py`**: Resume analysis endpoints
  - `/analyze`: Analyze resume against job description
  - `/history`: Get analysis history

- **`models.py`**: Data models
  - `ResumeData`: Resume input data
  - `JobDescriptionData`: Job description data
  - `ResumeAnalysisResponse`: Analysis results

#### **Interview Scheduler Agent** (`agents/interview_scheduler/`)
- **`agent.py`**: Interview scheduling logic
  - Calendar integration
  - Email template management
  - Interview slot management
  - Candidate tracking

- **`api.py`**: Interview endpoints
  - `/schedule`: Schedule new interviews
  - `/templates`: Get email templates
  - `/slots`: Get available time slots

- **`models.py`**: Data models
  - `CandidateData`: Candidate information
  - `InterviewDetails`: Interview requirements
  - `InterviewResponse`: Scheduling results

### 3. **Data Storage**

#### **File Structure** (`data/`)
```
data/
├── job_descriptions/           # Generated job descriptions
│   ├── doctor_imercfy_20250825_162531_job_description.txt
│   └── software_engineer_techcorp_20250825_163045_job_description.txt
├── resumes/                    # Uploaded resume files
│   ├── john_doe_resume.pdf
│   └── jane_smith_resume.docx
├── analysis_results/           # Resume analysis results
│   ├── john_doe_analysis_20250825_164230.json
│   └── jane_smith_analysis_20250825_165045.json
├── email_templates/            # Email templates
│   ├── interview_invitation.html
│   ├── interview_confirmation.html
│   └── interview_reminder.html
└── scheduling/                 # Interview schedules
    ├── interviews_20250825.json
    └── calendar_events.json
```

## 🔧 Configuration Management

### **Environment Variables** (`.env`)
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Agent Ports
ROOT_AGENT_PORT=8000
JD_GENERATOR_PORT=8001
RESUME_ANALYZER_PORT=8002
INTERVIEW_SCHEDULER_PORT=8003

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### **Agent Configuration** (Each agent's `config.py`)
```python
class AgentConfig:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4')
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
        self.data_dir = os.getenv('DATA_DIR', 'data/')
```

## 🔄 API Communication Patterns

### 1. **Frontend → Root Agent**
```typescript
// frontend/src/services/api.ts
const rootAgentAPI = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 120000
})

// Example: Generate job description
export const generateJobDescription = async (jobDetails: JobDetails) => {
  const response = await rootAgentAPI.post('/jd/generate', jobDetails)
  return response.data
}
```

### 2. **Root Agent → Sub-Agents**
```python
# agents/root_agent/coordinator.py
def generate_job_description(self, job_details: Dict[str, Any]) -> Dict[str, Any]:
    try:
        result = self.jd_generator.generate_job_description(job_details)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': 'generation_failed',
            'message': f'Error generating JD: {str(e)}'
        }
```

### 3. **Sub-Agent Processing**
```python
# agents/jd_generator/agent.py
def generate_job_description(self, job_details: JobDetails) -> Dict[str, Any]:
    try:
        # LangChain processing
        prompt = self.create_jd_prompt(job_details)
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Format and return
        return {
            'success': True,
            'job_description': response.content,
            'metadata': job_details.model_dump()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

## 🚀 Service Startup

### **Automated Startup** (`start_services.py`)
```python
import subprocess
import time

def start_services():
    services = [
        ('Root Agent', 'agents.root_agent.api:app', 8000),
        ('JD Generator', 'agents.jd_generator.api:app', 8001),
        ('Resume Analyzer', 'agents.resume_analyzer.api:app', 8002),
        ('Interview Scheduler', 'agents.interview_scheduler.api:app', 8003)
    ]
    
    for name, app, port in services:
        subprocess.Popen([
            'python', '-m', 'uvicorn', app,
            '--host', '0.0.0.0', '--port', str(port)
        ])
        print(f"Started {name} on port {port}")
        time.sleep(2)
```

### **Manual Startup**
```bash
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

## 🔍 Error Handling & Logging

### **Frontend Error Handling**
```typescript
// frontend/src/services/api.ts
const handleApiError = (error: any) => {
  if (error.code === 'ECONNABORTED') {
    return 'Request timed out. Please try again.'
  } else if (error.response?.status === 422) {
    return 'Invalid data format. Please check your input.'
  } else if (error.response?.status === 500) {
    return 'Server error. Please try again later.'
  }
  return error.message || 'An unexpected error occurred.'
}
```

### **Backend Error Handling**
```python
# agents/root_agent/api.py
@app.post("/jd/generate")
async def generate_job_description(job_details: JobDetails):
    try:
        result = coordinator.generate_job_description(job_details.model_dump())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"JD generation failed: {str(e)}"
        )
```

## 📊 Data Models & Validation

### **Frontend TypeScript Interfaces**
```typescript
// frontend/src/services/api.ts
interface JobDetails {
  job_title: string
  company_name: string
  location: string
  salary: number
  experience: string
  education: string
  skills: string
  responsibilities: string
  requirements: string
  visa_required: boolean
  shift: string
  employment_type: string
}
```

### **Backend Pydantic Models**
```python
# agents/jd_generator/models.py
class JobDetails(BaseModel):
    job_title: str = Field(..., description="Job title")
    company_name: str = Field(..., description="Company name")
    experience_required: str = Field(..., description="Experience requirement")
    salary_range: str = Field(..., description="Salary range")
    location: str = Field(..., description="Job location")
    # ... other fields
```

## 🔒 Security Considerations

### **CORS Configuration**
```python
# All agent APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Input Validation**
- Pydantic models for all API inputs
- Type checking in TypeScript
- File upload restrictions
- Environment variable validation

### **Error Handling**
- Comprehensive try-catch blocks
- Meaningful error messages
- Proper HTTP status codes
- Logging for debugging

## 🎯 Key Design Principles

### 1. **Modularity**
- Each agent is independent and deployable
- Clear separation of concerns
- Plug-and-play architecture

### 2. **Scalability**
- Microservices architecture
- Independent scaling of agents
- Load balancing ready

### 3. **Maintainability**
- Clean code structure
- Comprehensive documentation
- Type safety throughout
- Consistent error handling

### 4. **User Experience**
- Modern, responsive UI
- Real-time feedback
- Progressive loading
- Error recovery

### 5. **Reliability**
- Robust error handling
- Data validation
- Graceful degradation
- Health monitoring

---

This structure provides a solid foundation for a scalable, maintainable, and user-friendly HR automation system.
