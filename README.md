# 🤖 HR Agent Suite

**AI-Powered HR Automation Suite with Root Agent Architecture**

A sophisticated HR automation system that uses a root agent to coordinate multiple specialized sub-agents for job description generation and resume analysis.

## 🏗️ Architecture Overview

The HR Agent Suite follows a **Root Agent Architecture** where a central coordinator manages all sub-agents:

```
HR Root Agent (Coordinator)
├── JD Generator Agent
├── Resume Analyzer Agent
└── Utility Services
    ├── File Manager
    ├── Config Manager
    └── Data Storage
```

## 📁 Project Structure

```
hr-agent/
├── agents/                          # All agent modules
│   ├── root_agent/                  # Main coordinator agent
│   │   ├── __init__.py
│   │   └── hr_root_agent.py         # Root agent implementation
│   ├── jd_generator/                # Job Description Generator
│   │   ├── __init__.py
│   │   └── jd_generator_agent.py    # JD generation logic
│   ├── resume_analyzer/             # Resume Analyzer
│   │   ├── __init__.py
│   │   └── resume_analyzer_agent.py # Resume analysis logic
│   └── interview_scheduler/         # Interview Scheduler
│       ├── __init__.py
│       └── interview_scheduler_agent.py # Interview scheduling logic
├── data/                            # Data storage
│   ├── job_descriptions/            # Generated job descriptions
│   ├── resumes/                     # Uploaded resumes
│   └── analysis_results/            # Analysis results
├── utils/                           # Utility modules
│   ├── __init__.py
│   ├── file_manager.py              # File operations
│   └── config_manager.py            # Configuration management
├── config/                          # Configuration files
│   └── config.json                  # System configuration
├── ui/                              # User interface
│   ├── hr_agent_ui.py               # Main Streamlit web UI
│   └── interview_scheduler_ui.py    # Interview scheduler UI
├── docs/                            # Documentation
│   └── INTERVIEW_SCHEDULER.md       # Interview scheduler documentation
├── main.py                          # CLI application entry point
├── requirements.txt                 # Python dependencies
├── env_example.txt                  # Environment variables template
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

## 🚀 Features

### 🤖 Root Agent (Coordinator)
- **Central Management**: Coordinates all sub-agents
- **System Status**: Monitors agent health and system status
- **Data Management**: Handles file operations and data persistence
- **Configuration**: Manages system settings and configurations
- **Error Handling**: Centralized error handling and recovery

### 📝 Job Description Generator Agent
- **AI-Powered Generation**: Uses GPT-4 for professional JD creation
- **Structured Output**: Organized into clear sections:
  - Job Overview
  - **4-6 Core Responsibilities** (focused and impactful)
  - **Three-Category Qualifications**:
    - Education & Certifications
    - Technical Skills
    - Soft Skills & Competencies
  - **4-6 Key Benefits** (quality over quantity)
- **Industry-Specific**: Tailored to different industries and roles
- **Inclusive Language**: Uses inclusive and engaging language

### 📊 Resume Analyzer Agent
- **Multi-Format Support**: PDF, DOCX, TXT, JPG, JPEG (with OCR)
- **Comprehensive Analysis**: 100-point scoring system
- **Three-Dimensional Scoring**:
  - Skills Match (40% weight)
  - Experience Relevance (35% weight)
  - Formatting Quality (25% weight)
- **Detailed Feedback**: Strengths, weaknesses, and recommendations
- **Input Validation**: Robust validation to prevent false scores

### 🛠️ Utility Services
- **File Manager**: Handles all file operations and data persistence
- **Config Manager**: Manages system configuration and settings
- **Data Organization**: Structured data storage and retrieval

## 🎯 Key Improvements

### ✅ **Perfect Folder Structure**
- **Modular Design**: Each agent in its own directory
- **Clear Separation**: Agents, utilities, data, and UI separated
- **Scalable Architecture**: Easy to add new agents or features

### ✅ **Root Agent Coordination**
- **Single Point of Control**: All operations go through the root agent
- **Centralized Management**: System status, configuration, and data management
- **Better Error Handling**: Centralized error handling and recovery

### ✅ **Enhanced Job Descriptions**
- **Focused Content**: 4-6 core responsibilities instead of 6-8
- **Structured Qualifications**: Three clear categories
- **Concise Benefits**: 4-6 key benefits instead of comprehensive lists

### ✅ **Improved Resume Analysis**
- **Better Validation**: More lenient input validation
- **Accurate Scoring**: Fixed scoring issues for legitimate content
- **Multi-Format Support**: PDF, DOCX, TXT, JPG, JPEG with OCR

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API key
- Tesseract OCR (for image processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hr-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env and add your OpenAI API key
   ```

4. **Install Tesseract OCR** (for image processing)
   - **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

### Usage

#### 🖥️ **CLI Application**
```bash
python main.py
```

#### 🌐 **Web Interface**
```bash
python -m streamlit run ui/hr_agent_ui.py --server.port 8501
```

## 📋 Usage Examples

### Generate Job Description
1. Navigate to "Generate Job Description"
2. Fill in job details (title, company, experience, etc.)
3. Click "Generate Job Description"
4. Review and save the generated JD

### Analyze Resume
1. Navigate to "Analyze Resume"
2. Select a saved job description
3. Upload resume file (PDF, DOCX, TXT, JPG, JPEG)
4. Click "Analyze Resume"
5. Review detailed analysis results

## 🔧 Configuration

The system uses a centralized configuration system:

```json
{
  "system": {
    "name": "HR Agent Suite",
    "version": "1.0.0"
  },
  "agents": {
    "jd_generator": {
      "enabled": true,
      "model": "gpt-4",
      "temperature": 0.7
    },
    "resume_analyzer": {
      "enabled": true,
      "model": "gpt-4",
      "temperature": 0.3
    }
  },
  "analysis": {
    "score_weights": {
      "skills": 0.4,
      "experience": 0.35,
      "formatting": 0.25
    }
  }
}
```

## 📊 Data Storage

### Job Descriptions
- **Location**: `data/job_descriptions/`
- **Format**: `.txt` files with corresponding `.json` metadata
- **Naming**: `{job_title}_{company_name}_job_description.txt`

### Resumes
- **Location**: `data/resumes/`
- **Format**: `.txt` files
- **Support**: PDF, DOCX, TXT, JPG, JPEG

### Analysis Results
- **Location**: `data/analysis_results/`
- **Format**: `.json` files with detailed analysis
- **Naming**: `{candidate_name}_analysis_{timestamp}.json`

## 🔍 System Status

The root agent provides comprehensive system status:

- **Agent Health**: Status of all sub-agents
- **Data Statistics**: File counts and storage information
- **Configuration**: Current system settings
- **Error Logging**: Centralized error tracking

## 🛠️ Development

### Adding New Agents
1. Create new directory in `agents/`
2. Implement agent logic
3. Register with root agent
4. Update configuration

### Extending Functionality
1. Modify root agent for new coordination logic
2. Update utility services as needed
3. Extend UI for new features
4. Update configuration schema

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the configuration guide

---

**🎉 Welcome to the HR Agent Suite - Where AI Meets HR Excellence!** 