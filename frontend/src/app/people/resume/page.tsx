'use client'

import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Button,
  Card,
  CardBody,
  FormControl,
  FormLabel,
  Select,
  Input,
  useToast,
  Badge,
  Icon,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
} from '@chakra-ui/react'
import { 
  Upload, 
  FileText, 
  BarChart3,
  Download,
  Eye,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import MainLayout from '@/components/Layout/MainLayout'
import { rootAgentService } from '@/services/api'

interface ResumeAnalysis {
  id: string
  candidate_name: string
  job_title: string
  score: number
  date: string
  status: string
}

interface AnalysisResult {
  score: number
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
  skills_match: { skill: string; match: boolean }[]
  job_skills: string[]
}

interface JobDescription {
  id: string
  title: string
  company: string
  filename: string
  created_at: string
  job_title?: string
  company_name?: string
  content?: string
}

export default function ResumeAnalyzerPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedJobDescription, setSelectedJobDescription] = useState('')
  const [jobDescriptions, setJobDescriptions] = useState<JobDescription[]>([])
  const [analysisHistory, setAnalysisHistory] = useState<ResumeAnalysis[]>([])
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult | null>(null)
  const [analyzing, setAnalyzing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const toast = useToast()

  useEffect(() => {
    loadJobDescriptions()
    loadAnalysisHistory()
  }, [])

  const loadJobDescriptions = async () => {
    try {
      const response = await rootAgentService.getJobDescriptions()
      // Backend returns array directly, not wrapped in job_descriptions property
      const jobDescriptionsData = Array.isArray(response) ? response : (response.job_descriptions || [])
      
      // Transform the data to match the frontend interface
      const transformedJobDescriptions = jobDescriptionsData.map((jd: any) => ({
        id: jd.filename,
        title: jd.metadata?.job_title || jd.filename,
        company: jd.metadata?.company_name || 'Unknown Company',
        filename: jd.filename,
        created_at: jd.metadata?.created_at || jd.metadata?.generated_at || new Date().toISOString(),
        job_title: jd.metadata?.job_title,
        company_name: jd.metadata?.company_name,
        content: jd.content || '' // Include the job description content
      }))
      
      setJobDescriptions(transformedJobDescriptions)
    } catch (error) {
      console.error('Failed to load job descriptions:', error)
    }
  }

  const loadAnalysisHistory = async () => {
    try {
      const response = await rootAgentService.getAnalysisHistory()
      setAnalysisHistory(response.history || [])
    } catch (error) {
      console.error('Failed to load analysis history:', error)
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile || !selectedJobDescription) {
      toast({
        title: 'Error',
        description: 'Please select both a resume file and a job description',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
      return
    }

    try {
      setAnalyzing(true)
      
      // Find the selected job description
      const jobDesc = jobDescriptions.find(jd => jd.filename === selectedJobDescription)
      if (!jobDesc) {
        throw new Error('Selected job description not found')
      }

      // Create resume data
      const resumeData = {
        content: await readFileContent(selectedFile),
        candidate_name: selectedFile.name.split('.')[0],
        candidate_email: '',
        file_name: selectedFile.name,
      }

      // Create job description data in the correct format
      const jobDescriptionData = {
        content: jobDesc.content || '', // We need to get the actual content
        job_title: jobDesc.job_title || jobDesc.title || '',
        company_name: jobDesc.company_name || jobDesc.company || '',
      }
      
      // Debug logging
      console.log('Job Description Data:', jobDescriptionData)
      console.log('Resume Data:', resumeData)

      // Analyze resume
      const response = await rootAgentService.analyzeResume(resumeData, jobDescriptionData)
      
      if (response.success) {
        // Extract data from the nested analysis_result object
        const analysisResult = response.analysis_result || response
        setCurrentAnalysis({
          score: analysisResult.overall_score || 0,
          strengths: analysisResult.strengths || [],
          weaknesses: analysisResult.weaknesses || [],
          recommendations: analysisResult.recommendations || [],
          skills_match: analysisResult.skills_analysis?.resume_skills?.map((skill: string) => ({
            skill: skill,
            match: analysisResult.skills_analysis?.job_skills?.includes(skill) || false
          })) || [],
          job_skills: analysisResult.skills_analysis?.job_skills || [],
        })
        
        toast({
          title: 'Success',
          description: 'Resume analyzed successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
        
        // Reload analysis history
        await loadAnalysisHistory()
      } else {
        throw new Error(response.message || 'Analysis failed')
      }
    } catch (error) {
      console.error('Analysis failed:', error)
      toast({
        title: 'Error',
        description: 'Failed to analyze resume',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setAnalyzing(false)
    }
  }

  const readFileContent = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string
        resolve(content)
      }
      reader.onerror = reject
      reader.readAsText(file)
    })
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'green'
    if (score >= 60) return 'yellow'
    return 'red'
  }

  const getScoreIcon = (score: number) => {
    if (score >= 80) return CheckCircle
    if (score >= 60) return Clock
    return AlertCircle
  }

  return (
    <MainLayout>
      <Box p={8}>
        {/* Header */}
        <VStack spacing={6} align="stretch" mb={8}>
          <Heading size="lg" color="gray.800">
            Resume Analyzer
          </Heading>
          
          <Text color="gray.600" fontSize="lg">
            Upload candidate resumes and analyze them against job descriptions using AI-powered insights.
          </Text>
        </VStack>

        <VStack spacing={8} align="stretch">
          {/* Upload Section */}
          <Card>
            <CardBody>
              <VStack spacing={6} align="stretch">
                <Heading size="md" color="brand.500">Upload Resume</Heading>
                
                <HStack spacing={6}>
                  {/* File Upload */}
                  <VStack spacing={4} align="start" flex={1}>
                    <FormControl>
                      <FormLabel>Resume File</FormLabel>
                      <Input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf,.docx,.txt"
                        onChange={handleFileSelect}
                        display="none"
                      />
                      <Button
                        leftIcon={<Icon as={Upload} />}
                        onClick={() => fileInputRef.current?.click()}
                        variant="outline"
                        w="full"
                      >
                        {selectedFile ? selectedFile.name : 'Choose File'}
                      </Button>
                    </FormControl>
                  </VStack>

                  {/* Job Description Selection */}
                  <VStack spacing={4} align="start" flex={1}>
                    <FormControl>
                      <FormLabel>Job Description</FormLabel>
                      <Select
                        value={selectedJobDescription}
                        onChange={(e) => setSelectedJobDescription(e.target.value)}
                        placeholder="Select a job description"
                      >
                        {jobDescriptions.map((jd) => (
                          <option key={jd.filename} value={jd.filename}>
                            {jd.job_title || jd.title} - {jd.company_name || jd.company}
                          </option>
                        ))}
                      </Select>
                    </FormControl>
                  </VStack>
                </HStack>

                <Button
                  leftIcon={<Icon as={BarChart3} />}
                  colorScheme="brand"
                  onClick={handleAnalyze}
                  isLoading={analyzing}
                  loadingText="Analyzing..."
                  isDisabled={!selectedFile || !selectedJobDescription}
                >
                  Analyze Resume
                </Button>
              </VStack>
            </CardBody>
          </Card>

          {/* Analysis Results */}
          {currentAnalysis && (
            <Card>
              <CardBody>
                <VStack spacing={6} align="stretch">
                  <Heading size="md" color="brand.500">Analysis Results</Heading>
                  
                                     {/* Score Overview */}
                   <VStack spacing={6} align="stretch">
                     {/* Main Score Display */}
                     <Box textAlign="center" py={4} bg={`${getScoreColor(currentAnalysis.score)}.50`} borderRadius="lg">
                       <Icon 
                         as={getScoreIcon(currentAnalysis.score)} 
                         color={`${getScoreColor(currentAnalysis.score)}.500`}
                         boxSize={12}
                         mb={2}
                       />
                       <Text fontSize="4xl" fontWeight="bold" color={`${getScoreColor(currentAnalysis.score)}.500`}>
                         {currentAnalysis.score}%
                       </Text>
                       <Text fontSize="lg" color="gray.600" fontWeight="medium">Overall Match Score</Text>
                     </Box>
                     
                     {/* Analysis Details Grid */}
                     <HStack spacing={8} align="start">
                       {/* Strengths */}
                       <VStack spacing={3} align="start" flex={1} bg="green.50" p={4} borderRadius="lg">
                         <Text fontWeight="bold" color="green.700" fontSize="lg">✅ Strengths</Text>
                         <VStack spacing={2} align="start" w="full">
                           {currentAnalysis.strengths.slice(0, 4).map((strength, index) => (
                             <HStack key={index} w="full">
                               <Icon as={CheckCircle} color="green.500" boxSize={4} />
                               <Text fontSize="sm" color="gray.700">{strength}</Text>
                             </HStack>
                           ))}
                         </VStack>
                       </VStack>
                       
                       {/* Areas for Improvement */}
                       <VStack spacing={3} align="start" flex={1} bg="orange.50" p={4} borderRadius="lg">
                         <Text fontWeight="bold" color="orange.700" fontSize="lg">⚠️ Areas for Improvement</Text>
                         <VStack spacing={2} align="start" w="full">
                           {currentAnalysis.weaknesses.slice(0, 4).map((weakness, index) => (
                             <HStack key={index} w="full">
                               <Icon as={AlertCircle} color="orange.500" boxSize={4} />
                               <Text fontSize="sm" color="gray.700">{weakness}</Text>
                             </HStack>
                           ))}
                         </VStack>
                       </VStack>
                     </HStack>
                   </VStack>

                                     {/* Skills Match */}
                   {currentAnalysis.skills_match.length > 0 && (
                     <VStack spacing={4} align="stretch">
                       <Text fontWeight="bold" fontSize="lg" color="gray.700">🔧 Skills Analysis</Text>
                       
                       {/* Skills Overview */}
                       <VStack spacing={4} align="stretch">
                         <HStack spacing={4} align="start">
                         {/* Resume Skills */}
                         <VStack spacing={3} align="start" flex={1} bg="blue.50" p={4} borderRadius="lg">
                           <Text fontWeight="bold" color="blue.700">📄 Resume Skills</Text>
                           <VStack spacing={2} align="start" w="full">
                             {currentAnalysis.skills_match.slice(0, 6).map((skill, index) => (
                               <HStack key={index} w="full" justify="space-between">
                                 <Text fontSize="sm" color="gray.700">{skill.skill}</Text>
                                 <Badge 
                                   colorScheme={skill.match ? 'green' : 'gray'} 
                                   size="sm"
                                 >
                                   {skill.match ? '✓ Match' : '✗ Missing'}
                                 </Badge>
                               </HStack>
                             ))}
                           </VStack>
                         </VStack>
                         
                         {/* Job Skills */}
                         <VStack spacing={3} align="start" flex={1} bg="green.50" p={4} borderRadius="lg">
                           <Text fontWeight="bold" color="green.700">🎯 Required Job Skills</Text>
                           <VStack spacing={2} align="start" w="full">
                             {currentAnalysis.job_skills.slice(0, 6).map((skill, index) => (
                               <HStack key={index} w="full" justify="space-between">
                                 <Text fontSize="sm" color="gray.700">{skill}</Text>
                                 <Badge 
                                   colorScheme={currentAnalysis.skills_match.some(s => s.skill === skill) ? 'green' : 'red'} 
                                   size="sm"
                                 >
                                   {currentAnalysis.skills_match.some(s => s.skill === skill) ? '✓ Found' : '✗ Missing'}
                                 </Badge>
                               </HStack>
                             ))}
                           </VStack>
                         </VStack>
                         </HStack>
                         
                         {/* Skills Match Summary */}
                         <VStack spacing={3} align="start" bg="purple.50" p={4} borderRadius="lg">
                           <Text fontWeight="bold" color="purple.700">📊 Match Summary</Text>
                           <VStack spacing={2} align="start" w="full">
                             <HStack justify="space-between" w="full">
                               <Text fontSize="sm" color="gray.700">Total Skills:</Text>
                               <Text fontSize="sm" fontWeight="bold">{currentAnalysis.skills_match.length}</Text>
                             </HStack>
                             <HStack justify="space-between" w="full">
                               <Text fontSize="sm" color="gray.700">Matched Skills:</Text>
                               <Text fontSize="sm" fontWeight="bold" color="green.600">
                                 {currentAnalysis.skills_match.filter(s => s.match).length}
                               </Text>
                             </HStack>
                             <HStack justify="space-between" w="full">
                               <Text fontSize="sm" color="gray.700">Missing Skills:</Text>
                               <Text fontSize="sm" fontWeight="bold" color="red.600">
                                 {currentAnalysis.skills_match.filter(s => !s.match).length}
                               </Text>
                             </HStack>
                             <HStack justify="space-between" w="full">
                               <Text fontSize="sm" color="gray.700">Match Rate:</Text>
                               <Text fontSize="sm" fontWeight="bold" color="blue.600">
                                 {Math.round((currentAnalysis.skills_match.filter(s => s.match).length / currentAnalysis.skills_match.length) * 100)}%
                               </Text>
                             </HStack>
                           </VStack>
                         </VStack>
                       </VStack>
                     </VStack>
                   )}

                                     {/* Recommendations */}
                   {currentAnalysis.recommendations.length > 0 && (
                     <VStack spacing={4} align="stretch">
                       <Text fontWeight="bold" fontSize="lg" color="gray.700">💡 Recommendations</Text>
                       <Box bg="teal.50" p={4} borderRadius="lg">
                         <VStack spacing={3} align="start">
                           {currentAnalysis.recommendations.slice(0, 5).map((rec, index) => (
                             <HStack key={index} align="start" w="full">
                               <Icon as={CheckCircle} color="teal.500" boxSize={4} mt={0.5} />
                               <Text fontSize="sm" color="gray.700" flex={1}>{rec}</Text>
                             </HStack>
                           ))}
                         </VStack>
                       </Box>
                     </VStack>
                   )}
                </VStack>
              </CardBody>
            </Card>
          )}

          {/* Analysis History */}
          <Card>
            <CardBody>
              <VStack spacing={6} align="stretch">
                <Heading size="md" color="brand.500">Analysis History</Heading>
                
                {analysisHistory.length > 0 ? (
                  <TableContainer>
                    <Table>
                      <Thead>
                        <Tr>
                          <Th>Candidate</Th>
                          <Th>Job Title</Th>
                          <Th>Score</Th>
                          <Th>Date</Th>
                          <Th>Status</Th>
                          <Th>Actions</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {analysisHistory.map((analysis) => (
                          <Tr key={analysis.id}>
                            <Td>{analysis.candidate_name}</Td>
                            <Td>{analysis.job_title}</Td>
                            <Td>
                              <Badge colorScheme={getScoreColor(analysis.score)}>
                                {analysis.score}%
                              </Badge>
                            </Td>
                            <Td>{analysis.date}</Td>
                            <Td>
                              <Badge colorScheme={analysis.status === 'completed' ? 'green' : 'yellow'}>
                                {analysis.status}
                              </Badge>
                            </Td>
                            <Td>
                              <HStack spacing={2}>
                                <Button size="sm" variant="ghost">
                                  <Icon as={Eye} boxSize={4} />
                                </Button>
                                <Button size="sm" variant="ghost">
                                  <Icon as={Download} boxSize={4} />
                                </Button>
                              </HStack>
                            </Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Box textAlign="center" py={8} color="gray.500">
                    <Icon as={FileText} boxSize={12} mb={4} />
                    <Text>No analysis history yet</Text>
                    <Text fontSize="sm">Upload and analyze resumes to see history here.</Text>
                  </Box>
                )}
              </VStack>
            </CardBody>
          </Card>
        </VStack>
      </Box>
    </MainLayout>
  )
}
