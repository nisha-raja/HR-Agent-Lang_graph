import axios from 'axios'

// Helper function to map experience levels to backend format
const mapExperienceLevel = (level: string): string => {
  switch (level) {
    case 'Junior':
      return '0-2 years'
    case 'Mid-level':
      return '3-5 years'
    case 'Senior':
      return '5-8 years'
    case 'Lead':
      return '8-10 years'
    case 'Manager':
      return '10+ years'
    default:
      return '3-5 years' // Default to mid-level
  }
}

// TypeScript interfaces
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
  skills_required: string
  work_location_type: string
}

interface ResumeData {
  content: string
  candidate_name: string
  candidate_email: string
  file_name: string
}

interface JobDescriptionData {
  id: string
  title: string
  company: string
  filename: string
  created_at: string
  content?: string
}

interface CandidateData {
  name: string
  email: string
  phone: string
  position: string
  experience: number
  resume_score?: number
}

interface InterviewDetails {
  date: string
  time: string
  duration: number
  type: string
  interviewer: string
  location: string
}

// API base URLs
const ROOT_AGENT_URL = 'http://localhost:8000'
const JD_GENERATOR_URL = 'http://localhost:8001'
const RESUME_ANALYZER_URL = 'http://localhost:8002'
const INTERVIEW_SCHEDULER_URL = 'http://localhost:8003'

// Create axios instances
const rootAgentAPI = axios.create({
  baseURL: ROOT_AGENT_URL,
  timeout: 120000, // Increased to 2 minutes for JD generation
})

const jdGeneratorAPI = axios.create({
  baseURL: JD_GENERATOR_URL,
  timeout: 120000, // Increased to 2 minutes for JD generation
})

const resumeAnalyzerAPI = axios.create({
  baseURL: RESUME_ANALYZER_URL,
  timeout: 60000, // 1 minute for resume analysis
})

const interviewSchedulerAPI = axios.create({
  baseURL: INTERVIEW_SCHEDULER_URL,
  timeout: 60000, // 1 minute for interview scheduling
})

// Root Agent API calls
export const rootAgentService = {
  // Health check
  getHealth: async () => {
    const response = await rootAgentAPI.get('/health')
    return response.data
  },

  // Get all agents
  getAgents: async () => {
    const response = await rootAgentAPI.get('/agents')
    return response.data
  },

  // Get agent status
  getAgentStatus: async (agentName: string) => {
    const response = await rootAgentAPI.get(`/agents/${agentName}/status`)
    return response.data
  },

  // AI Assistant
  aiAssistant: async (query: string) => {
    const response = await rootAgentAPI.post('/ai/assist', { query })
    return response.data
  },

  // JD Generator routes
  generateJobDescription: async (jobDetails: JobDetails) => {
    // Transform frontend job details to match backend expectations
    const transformedJobDetails = {
      job_title: jobDetails.job_title,
      company_name: jobDetails.company_name,
      experience_required: mapExperienceLevel(jobDetails.experience), // Map experience to experience_required
      employment_type: jobDetails.employment_type,
      salary_range: `$${jobDetails.salary}`, // Map salary to salary_range
      industry: jobDetails.industry || 'Technology',
      location: jobDetails.location,
      department: jobDetails.department || 'General',
      education: jobDetails.education,
      skills: jobDetails.skills,
      responsibilities: jobDetails.responsibilities,
      requirements: jobDetails.requirements,
      visa_required: jobDetails.visa_required,
      shift: jobDetails.shift,
      skills_required: jobDetails.skills_required || '',
      work_location_type: jobDetails.work_location_type || 'Remote'
    }
    const response = await rootAgentAPI.post('/jd/generate', transformedJobDetails)
    return response.data
  },

  saveJobDescription: async (jobDetails: JobDetails, description: string) => {
    // Transform frontend job details to match backend expectations
    const transformedJobDetails = {
      job_title: jobDetails.job_title,
      company_name: jobDetails.company_name,
      experience_required: mapExperienceLevel(jobDetails.experience), // Map experience to experience_required
      employment_type: jobDetails.employment_type,
      salary_range: `$${jobDetails.salary}`, // Map salary to salary_range
      industry: jobDetails.industry || 'Technology',
      location: jobDetails.location,
      department: jobDetails.department || 'General',
      education: jobDetails.education,
      skills: jobDetails.skills,
      responsibilities: jobDetails.responsibilities,
      requirements: jobDetails.requirements,
      visa_required: jobDetails.visa_required,
      shift: jobDetails.shift,
      skills_required: jobDetails.skills_required || '',
      work_location_type: jobDetails.work_location_type || 'Remote'
    }
    const response = await rootAgentAPI.post('/jd/save', { job_details: transformedJobDetails, description })
    return response.data
  },

  getJobDescriptions: async () => {
    const response = await rootAgentAPI.get('/jd/list')
    return response.data
  },

  deleteJobDescription: async (filename: string) => {
    const response = await rootAgentAPI.delete(`/jd/${filename}`)
    return response.data
  },

  // Resume Analyzer routes
  analyzeResume: async (resumeData: ResumeData, jobDescriptionData: JobDescriptionData) => {
    const response = await rootAgentAPI.post('/resume/analyze', { resume_data: resumeData, job_description_data: jobDescriptionData })
    return response.data
  },

  getAnalysisHistory: async () => {
    const response = await rootAgentAPI.get('/resume/history')
    return response.data
  },

  // Interview Scheduler routes
  scheduleInterview: async (candidateData: CandidateData, interviewDetails: InterviewDetails) => {
    const response = await rootAgentAPI.post('/interview/schedule', { candidate_data: candidateData, interview_details: interviewDetails })
    return response.data
  },

  processCandidate: async (candidateData: CandidateData) => {
    const response = await rootAgentAPI.post('/interview/process-candidate', candidateData)
    return response.data
  },

  getEmailTemplates: async () => {
    const response = await rootAgentAPI.get('/interview/templates')
    return response.data
  },

  suggestInterviewSlots: async (date: string, duration?: number) => {
    const response = await rootAgentAPI.get('/interview/slots', { params: { date, duration } })
    return response.data
  },
}

// Direct JD Generator API calls
export const jdGeneratorService = {
  generate: async (jobDetails: JobDetails) => {
    // Transform frontend job details to match backend expectations
    const transformedJobDetails = {
      job_title: jobDetails.job_title,
      company_name: jobDetails.company_name,
      experience_required: mapExperienceLevel(jobDetails.experience), // Map experience to experience_required
      employment_type: jobDetails.employment_type,
      salary_range: `$${jobDetails.salary}`, // Map salary to salary_range
      industry: jobDetails.industry || 'Technology',
      location: jobDetails.location,
      department: jobDetails.department || 'General',
      education: jobDetails.education,
      skills: jobDetails.skills,
      responsibilities: jobDetails.responsibilities,
      requirements: jobDetails.requirements,
      visa_required: jobDetails.visa_required,
      shift: jobDetails.shift,
      skills_required: jobDetails.skills_required || '',
      work_location_type: jobDetails.work_location_type || 'Remote'
    }
    const response = await jdGeneratorAPI.post('/generate', { job_details: transformedJobDetails })
    return response.data
  },

  save: async (jobDetails: JobDetails, description: string) => {
    // Transform frontend job details to match backend expectations
    const transformedJobDetails = {
      job_title: jobDetails.job_title,
      company_name: jobDetails.company_name,
      experience_required: mapExperienceLevel(jobDetails.experience), // Map experience to experience_required
      employment_type: jobDetails.employment_type,
      salary_range: `$${jobDetails.salary}`, // Map salary to salary_range
      industry: jobDetails.industry || 'Technology',
      location: jobDetails.location,
      department: jobDetails.department || 'General',
      education: jobDetails.education,
      skills: jobDetails.skills,
      responsibilities: jobDetails.responsibilities,
      requirements: jobDetails.requirements,
      visa_required: jobDetails.visa_required,
      shift: jobDetails.shift
    }
    const response = await jdGeneratorAPI.post('/save', { job_details: transformedJobDetails, description })
    return response.data
  },

  list: async () => {
    const response = await jdGeneratorAPI.get('/list')
    return response.data
  },

  delete: async (filename: string) => {
    const response = await jdGeneratorAPI.delete(`/delete/${filename}`)
    return response.data
  },

  getStatus: async () => {
    const response = await jdGeneratorAPI.get('/status')
    return response.data
  },
}

// Direct Resume Analyzer API calls
export const resumeAnalyzerService = {
  analyze: async (resumeData: ResumeData, jobDescriptionData: JobDescriptionData) => {
    const response = await resumeAnalyzerAPI.post('/analyze', { resume_data: resumeData, job_description_data: jobDescriptionData })
    return response.data
  },

  analyzeUpload: async (file: File, jobDescriptionData?: JobDescriptionData) => {
    const formData = new FormData()
    formData.append('resume_file', file)
    if (jobDescriptionData) {
      formData.append('job_description_data', JSON.stringify(jobDescriptionData))
    }
    
    const response = await resumeAnalyzerAPI.post('/analyze-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  getHistory: async () => {
    const response = await resumeAnalyzerAPI.get('/history')
    return response.data
  },

  getStatus: async () => {
    const response = await resumeAnalyzerAPI.get('/status')
    return response.data
  },
}

// Direct Interview Scheduler API calls
export const interviewSchedulerService = {
  schedule: async (candidateData: CandidateData, interviewDetails: InterviewDetails) => {
    const response = await interviewSchedulerAPI.post('/schedule', { candidate_data: candidateData, interview_details: interviewDetails })
    return response.data
  },

  processCandidate: async (candidateData: CandidateData) => {
    const response = await interviewSchedulerAPI.post('/process-candidate', candidateData)
    return response.data
  },

  sendEmail: async (emailRequest: { to: string; subject: string; body: string }) => {
    const response = await interviewSchedulerAPI.post('/send-email', emailRequest)
    return response.data
  },

  getTemplates: async () => {
    const response = await interviewSchedulerAPI.get('/templates')
    return response.data
  },

  getTemplate: async (templateId: string) => {
    const response = await interviewSchedulerAPI.get(`/templates/${templateId}`)
    return response.data
  },

  getSlots: async (date: string, duration?: number) => {
    const response = await interviewSchedulerAPI.get('/slots', { params: { date, duration } })
    return response.data
  },

  getRecommendation: async (score: number) => {
    const response = await interviewSchedulerAPI.get(`/recommendation/${score}`)
    return response.data
  },

  validateSchedule: async (interviewDetails: InterviewDetails) => {
    const response = await interviewSchedulerAPI.post('/validate-schedule', interviewDetails)
    return response.data
  },

  getStatus: async () => {
    const response = await interviewSchedulerAPI.get('/status')
    return response.data
  },
}

// Utility functions
export const apiUtils = {
  // Check if all agents are healthy
  checkAllAgentsHealth: async () => {
    try {
      const health = await rootAgentService.getHealth()
      return health.status === 'healthy'
    } catch (error) {
      console.error('Health check failed:', error)
      return false
    }
  },

  // Parse AI assistant query and extract job details
  parseJobQuery: (query: string) => {
    const jobDetails: Partial<JobDetails> = {}
    
    // Extract salary
    const salaryMatch = query.match(/(\d+)\s*(?:salary|aed|usd)/i)
    if (salaryMatch) {
      jobDetails.salary = parseInt(salaryMatch[1])
    }
    
    // Extract experience
    const expMatch = query.match(/(\d+)\s*(?:year|yr)s?\s*experience/i)
    if (expMatch) {
      jobDetails.experience = expMatch[1] + ' years'
    }
    
    // Extract job title
    const titleMatch = query.match(/(doctor|surgeon|ent|general|nurse|engineer|developer|manager|analyst|consultant)/i)
    if (titleMatch) {
      jobDetails.job_title = titleMatch[1]
    }
    
    // Extract education
    if (query.toLowerCase().includes('master') || query.toLowerCase().includes('masters')) {
      jobDetails.education = 'Masters'
    } else if (query.toLowerCase().includes('bachelor') || query.toLowerCase().includes('bachelors')) {
      jobDetails.education = 'Bachelors'
    }
    
    // Extract visa requirement
    if (query.toLowerCase().includes('visa')) {
      jobDetails.visa_required = true
    }
    
    // Extract shift
    if (query.toLowerCase().includes('night shift')) {
      jobDetails.shift = 'Night'
    } else if (query.toLowerCase().includes('day shift')) {
      jobDetails.shift = 'Day'
    }
    
    return jobDetails
  },
}

export default {
  rootAgentService,
  jdGeneratorService,
  resumeAnalyzerService,
  interviewSchedulerService,
  apiUtils,
}
