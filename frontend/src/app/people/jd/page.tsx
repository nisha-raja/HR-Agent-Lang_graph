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
  Input,
  Select,
  useToast,
  Icon,
  Flex,
  useSteps,
  Step,
  StepIcon,
  StepIndicator,
  StepNumber,
  StepSeparator,
  StepStatus,
  StepTitle,
  Stepper,
  Progress,
  Spinner,
} from '@chakra-ui/react'
import { 
  ArrowLeft, 
  ArrowRight, 
  FileText,
  Save,
  Eye,
  Send,
  CheckCircle
} from 'lucide-react'
import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useForm, Controller } from 'react-hook-form'
import MainLayout from '@/components/Layout/MainLayout'
import { rootAgentService } from '@/services/api'

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

interface SavedJobDescription {
  id: string
  title: string
  company: string
  created_at: string
  filename: string
}

const steps = [
  { title: 'Basic Details', description: 'Job role and company info' },
  { title: 'Specific Details', description: 'Requirements and preferences' },
  { title: 'Preview & Validation', description: 'Review and finalize' },
  { title: 'Publish', description: 'Generate and save JD' },
]

function JobDescriptionPageContent() {
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [generatedJD, setGeneratedJD] = useState('')
  const [savedJDs, setSavedJDs] = useState<SavedJobDescription[]>([])
  const router = useRouter()
  const searchParams = useSearchParams()
  const toast = useToast()

  const { control, handleSubmit, setValue, formState: { errors } } = useForm<JobDetails>({
    defaultValues: {
      job_title: '',
      company_name: '',
      location: '',
      salary: 0,
      experience: '',
      education: '',
      skills: '',
      responsibilities: '',
      requirements: '',
      visa_required: false,
      shift: '',
      employment_type: 'Full time',
      skills_required: '',
      work_location_type: 'Remote',
    }
  })

  const { activeStep, setActiveStep } = useSteps({
    index: currentStep,
    count: steps.length,
  })

  useEffect(() => {
    // Load pre-filled data from URL if available
    const dataParam = searchParams.get('data')
    if (dataParam) {
      try {
        const jobDetails = JSON.parse(decodeURIComponent(dataParam))
        
        // Map backend field names to frontend field names
        const mappedJobDetails: any = {}
        Object.entries(jobDetails).forEach(([key, value]) => {
          if (key === 'experience_required') {
            mappedJobDetails['experience'] = value
          } else if (key === 'salary_range') {
            // Extract number from salary_range (e.g., "$5000" -> 5000)
            const salaryStr = String(value)
            const salaryMatch = salaryStr.match(/\$?(\d+)/)
            if (salaryMatch) {
              mappedJobDetails['salary'] = parseInt(salaryMatch[1])
            } else {
              mappedJobDetails['salary'] = 0
            }
          } else {
            mappedJobDetails[key] = value
          }
        })
        
        // Set the mapped values in the form
        Object.entries(mappedJobDetails).forEach(([key, value]) => {
          setValue(key as keyof JobDetails, value as string | number | boolean)
        })
        
        toast({
          title: 'Data Loaded',
          description: 'Job details have been pre-filled from your AI request',
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
      } catch (error) {
        console.error('Failed to parse job details:', error)
      }
    }

    // Load saved job descriptions
    loadSavedJDs()
  }, [searchParams, setValue, toast])

  const loadSavedJDs = async () => {
    try {
      const response = await rootAgentService.getJobDescriptions()
      // Backend returns array directly, not wrapped in job_descriptions property
      const jobDescriptionsData = Array.isArray(response) ? response : (response.job_descriptions || [])
      
      // Transform the data to match the frontend interface
      const transformedJobDescriptions = jobDescriptionsData.map((jd: any) => ({
        id: jd.filename,
        title: jd.metadata?.job_title || jd.filename,
        company: jd.metadata?.company_name || 'Unknown Company',
        created_at: jd.metadata?.created_at || jd.metadata?.generated_at || new Date().toISOString(),
        filename: jd.filename
      }))
      
      setSavedJDs(transformedJobDescriptions)
    } catch (error) {
      console.error('Failed to load saved JDs:', error)
    }
  }

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
      setActiveStep(currentStep + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
      setActiveStep(currentStep - 1)
    }
  }

  const generateJobDescription = async (data: JobDetails) => {
    try {
      setLoading(true)
      console.log('Generating JD with data:', data)
      
      const response = await rootAgentService.generateJobDescription(data)
      
      if (response.success) {
        setGeneratedJD(response.job_description)
        setCurrentStep(2) // Move to preview step
        setActiveStep(2)
        toast({
          title: 'Success',
          description: 'Job description generated successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
      } else {
        throw new Error(response.message || 'Failed to generate job description')
      }
    } catch (error: any) {
      console.error('Failed to generate JD:', error)
      
      let errorMessage = 'Failed to generate job description'
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. The AI is taking longer than expected. Please try again.'
      } else if (error.response?.status === 422) {
        errorMessage = 'Invalid data format. Please check your input fields.'
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error. Please try again later.'
      } else if (error.message) {
        errorMessage = error.message
      }
      
      toast({
        title: 'Error',
        description: errorMessage,
        status: 'error',
        duration: 8000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const saveJobDescription = async (data: JobDetails) => {
    try {
      setLoading(true)
      const response = await rootAgentService.saveJobDescription(data, generatedJD)
      
      if (response.success) {
        toast({
          title: 'Success',
          description: 'Job description saved successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
        await loadSavedJDs()
        setCurrentStep(3) // Move to publish step
        setActiveStep(3)
      } else {
        throw new Error(response.message || 'Failed to save job description')
      }
    } catch (error) {
      console.error('Failed to save JD:', error)
      toast({
        title: 'Error',
        description: 'Failed to save job description',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <Card>
            <CardBody>
              <VStack spacing={6} align="stretch">
                <Heading size="md" color="brand.500">Role Details</Heading>
                
                <HStack spacing={4}>
                  <FormControl isInvalid={!!errors.job_title}>
                    <FormLabel>Job Role</FormLabel>
                    <Controller
                      name="job_title"
                      control={control}
                      rules={{ required: 'Job title is required' }}
                      render={({ field }) => (
                        <Input {...field} placeholder="e.g., Senior Software Developer" />
                      )}
                    />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Seniority Level</FormLabel>
                    <Controller
                      name="experience"
                      control={control}
                      render={({ field }) => (
                        <Select {...field} placeholder="Select level">
                          <option value="Junior">Junior</option>
                          <option value="Mid-level">Mid-level</option>
                          <option value="Senior">Senior</option>
                          <option value="Lead">Lead</option>
                          <option value="Manager">Manager</option>
                        </Select>
                      )}
                    />
                  </FormControl>
                </HStack>

                <HStack spacing={4}>
                  <FormControl>
                    <FormLabel>Company Name</FormLabel>
                    <Controller
                      name="company_name"
                      control={control}
                      render={({ field }) => (
                        <Input {...field} placeholder="Enter company name" />
                      )}
                    />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Location</FormLabel>
                    <Controller
                      name="location"
                      control={control}
                      render={({ field }) => (
                        <Input {...field} placeholder="e.g., Dubai, UAE" />
                      )}
                    />
                  </FormControl>
                </HStack>

                <HStack spacing={4}>
                  <FormControl>
                    <FormLabel>Salary (AED)</FormLabel>
                    <Controller
                      name="salary"
                      control={control}
                      render={({ field }) => (
                        <Input 
                          {...field} 
                          type="number" 
                          placeholder="50000"
                          onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                        />
                      )}
                    />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Employment Type</FormLabel>
                    <Controller
                      name="employment_type"
                      control={control}
                      render={({ field }) => (
                        <Select {...field}>
                          <option value="Full time">Full time</option>
                          <option value="Part time">Part time</option>
                          <option value="Contract">Contract</option>
                          <option value="Freelance">Freelance</option>
                        </Select>
                      )}
                    />
                  </FormControl>
                </HStack>

                <HStack spacing={4}>
                  <FormControl>
                    <FormLabel>Work Location Type</FormLabel>
                    <Controller
                      name="work_location_type"
                      control={control}
                      render={({ field }) => (
                        <Select {...field}>
                          <option value="Remote">Remote</option>
                          <option value="On-site">On-site</option>
                          <option value="Hybrid">Hybrid</option>
                        </Select>
                      )}
                    />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Required Skills</FormLabel>
                    <Controller
                      name="skills_required"
                      control={control}
                      render={({ field }) => (
                        <Input {...field} placeholder="e.g., Python, Angular, Node.js, SQL" />
                      )}
                    />
                  </FormControl>
                </HStack>
              </VStack>
            </CardBody>
          </Card>
        )

      case 1:
        return (
          <Card>
            <CardBody>
              <VStack spacing={6} align="stretch">
                <Heading size="md" color="brand.500">Required Details</Heading>
                
                <HStack spacing={4}>
                  <FormControl>
                    <FormLabel>Education</FormLabel>
                    <Controller
                      name="education"
                      control={control}
                      render={({ field }) => (
                        <Input {...field} placeholder="e.g., Masters" />
                      )}
                    />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Experience</FormLabel>
                    <Controller
                      name="experience"
                      control={control}
                      render={({ field }) => (
                        <Input {...field} placeholder="e.g., 5+ Years, React" />
                      )}
                    />
                  </FormControl>
                </HStack>

                <FormControl>
                  <FormLabel>Skill Sets</FormLabel>
                  <Controller
                    name="skills"
                    control={control}
                    render={({ field }) => (
                      <Input {...field} placeholder="e.g., React, Angular" />
                    )}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Competencies</FormLabel>
                  <Controller
                    name="requirements"
                    control={control}
                    render={({ field }) => (
                      <Input {...field} placeholder="e.g., Business awareness" />
                    )}
                  />
                </FormControl>

                <HStack spacing={4}>
                  <FormControl>
                    <FormLabel>Visa Requirements</FormLabel>
                    <Controller
                      name="visa_required"
                      control={control}
                      render={({ field }) => (
                        <Select {...field} value={field.value ? 'true' : 'false'} onChange={(e) => field.onChange(e.target.value === 'true')}>
                          <option value="true">Yes</option>
                          <option value="false">No</option>
                        </Select>
                      )}
                    />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Shift</FormLabel>
                    <Controller
                      name="shift"
                      control={control}
                      render={({ field }) => (
                        <Select {...field} placeholder="Select shift">
                          <option value="Day">Day</option>
                          <option value="Night">Night</option>
                          <option value="Rotating">Rotating</option>
                        </Select>
                      )}
                    />
                  </FormControl>
                </HStack>
              </VStack>
            </CardBody>
          </Card>
        )

      case 2:
        return (
          <Card>
            <CardBody>
              <VStack spacing={6} align="stretch">
                <Flex justify="space-between" align="center">
                  <Heading size="md" color="brand.500">Job Preview</Heading>
                  <HStack spacing={2}>
                    <Button
                      leftIcon={<Icon as={Save} />}
                      colorScheme="brand"
                      onClick={handleSubmit(saveJobDescription)}
                      isLoading={loading}
                    >
                      Save as Draft
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Icon as={Eye} />
                    </Button>
                  </HStack>
                </Flex>

                {generatedJD ? (
                  <Box
                    p={4}
                    bg="gray.50"
                    borderRadius="md"
                    border="1px"
                    borderColor="gray.200"
                  >
                    <Text whiteSpace="pre-wrap">{generatedJD}</Text>
                  </Box>
                ) : (
                  <Box
                    p={8}
                    textAlign="center"
                    color="gray.500"
                  >
                    <Icon as={FileText} boxSize={12} mb={4} />
                    <Text>No job description generated yet</Text>
                    <Text fontSize="sm">
                      Fill in the details and click &ldquo;Generate JD with AI&rdquo; to create a customized job description.
                    </Text>
                  </Box>
                )}
              </VStack>
            </CardBody>
          </Card>
        )

      case 3:
        return (
          <Card>
            <CardBody>
              <VStack spacing={6} align="stretch">
                <Heading size="md" color="brand.500">Select publishing platform</Heading>
                
                <Button colorScheme="brand" size="lg">
                  Generate URL
                </Button>
                
                <HStack>
                  <Input 
                    value="https://thephoenixai.com/technology" 
                    readOnly 
                  />
                  <Button size="sm" variant="ghost">
                    Copy
                  </Button>
                </HStack>

                <VStack spacing={4} align="stretch">
                  {[
                    { name: 'LinkedIn', description: 'Professional network', enabled: true },
                    { name: 'Naukri', description: "India's job portal", enabled: false },
                    { name: 'Indeed', description: 'Global job search', enabled: false },
                    { name: 'Phoenixai', description: 'Global job search', enabled: true },
                  ].map((platform) => (
                    <HStack key={platform.name} justify="space-between" p={4} bg="gray.50" borderRadius="md">
                      <HStack>
                        <Text fontWeight="semibold">{platform.name}</Text>
                        <Text fontSize="sm" color="gray.600">{platform.description}</Text>
                      </HStack>
                      <Button
                        size="sm"
                        colorScheme={platform.enabled ? 'brand' : 'gray'}
                        variant={platform.enabled ? 'solid' : 'outline'}
                      >
                        {platform.enabled ? 'ON' : 'OFF'}
                      </Button>
                    </HStack>
                  ))}
                </VStack>
              </VStack>
            </CardBody>
          </Card>
        )

      default:
        return null
    }
  }

  return (
    <MainLayout>
      <Box p={8} position="relative">
        {/* Loading Overlay */}
        {loading && (
          <Box
            position="absolute"
            top={0}
            left={0}
            right={0}
            bottom={0}
            bg="rgba(255, 255, 255, 0.9)"
            zIndex={10}
            display="flex"
            alignItems="center"
            justifyContent="center"
            flexDirection="column"
            gap={4}
          >
            <Spinner size="xl" color="brand.500" />
            <Text fontSize="lg" fontWeight="medium" color="brand.500">
              Generating Job Description...
            </Text>
            <Text fontSize="sm" color="gray.600" textAlign="center">
              This may take up to 2 minutes as our AI creates a comprehensive job description
            </Text>
            <Progress size="sm" isIndeterminate colorScheme="brand" width="300px" />
          </Box>
        )}

        {/* Progress Stepper */}
        <VStack spacing={8} align="stretch" mb={8}>
          <Stepper index={activeStep} colorScheme="brand">
            {steps.map((step, index) => (
              <Step key={index}>
                <StepIndicator>
                  <StepStatus
                    complete={<StepIcon />}
                    incomplete={<StepNumber />}
                    active={<StepNumber />}
                  />
                </StepIndicator>
                <Box flexShrink="0">
                  <StepTitle>{step.title}</StepTitle>
                </Box>
                <StepSeparator />
              </Step>
            ))}
          </Stepper>
        </VStack>

        {/* Step Content */}
        {renderStepContent()}

        {/* Navigation */}
        <HStack justify="space-between" mt={8}>
          <Button
            leftIcon={<Icon as={ArrowLeft} />}
            onClick={handleBack}
            isDisabled={currentStep === 0}
            variant="outline"
          >
            Back
          </Button>

          <HStack spacing={4}>
            {currentStep === 0 && (
              <Button
                rightIcon={<Icon as={ArrowRight} />}
                onClick={handleSubmit(generateJobDescription)}
                isLoading={loading}
                loadingText="Generating JD..."
                colorScheme="brand"
              >
                Generate JD with AI
              </Button>
            )}
            
            {currentStep === 1 && (
              <Button
                rightIcon={<Icon as={ArrowRight} />}
                onClick={handleNext}
                colorScheme="brand"
              >
                Next
              </Button>
            )}
            
            {currentStep === 2 && (
              <Button
                rightIcon={<Icon as={Send} />}
                onClick={handleNext}
                colorScheme="brand"
              >
                Publish Now
              </Button>
            )}
            
            {currentStep === 3 && (
              <Button
                rightIcon={<Icon as={CheckCircle} />}
                colorScheme="green"
                onClick={() => router.push('/people')}
              >
                Done
              </Button>
            )}
          </HStack>
        </HStack>
      </Box>
    </MainLayout>
  )
}

export default function JobDescriptionPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <JobDescriptionPageContent />
    </Suspense>
  )
}
