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
  Textarea,
  useToast,
  Badge,
  Icon,
  Flex,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  SimpleGrid,
} from '@chakra-ui/react'
import { 
  Calendar, 
  Mail, 
  Plus,
  Eye,
  Edit,
  Send
} from 'lucide-react'
import { useState, useEffect } from 'react'
import MainLayout from '@/components/Layout/MainLayout'
import { rootAgentService } from '@/services/api'

interface Candidate {
  id: string
  name: string
  email: string
  job_title: string
  score: number
  status: string
}

interface Interview {
  id: string
  candidate_name: string
  job_title: string
  date: string
  time: string
  type: string
  status: string
}

interface EmailTemplate {
  template_id: string
  name: string
  subject: string
  template_type: string
}

export default function InterviewSchedulerPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [interviews, setInterviews] = useState<Interview[]>([])
  const [emailTemplates, setEmailTemplates] = useState<EmailTemplate[]>([])
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null)
  const [loading, setLoading] = useState(false)
  const [scheduling, setScheduling] = useState(false)
  const { isOpen, onOpen, onClose } = useDisclosure()
  const toast = useToast()

  // Form state for new interview
  const [interviewForm, setInterviewForm] = useState({
    candidate_name: '',
    candidate_email: '',
    job_title: '',
    interview_date: '',
    interview_time: '',
    interview_type: '',
    interviewer_name: '',
    interviewer_email: '',
    location: '',
    duration: '60',
    notes: '',
    email_template: '',
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      
      // Load candidates (mock data for now)
      setCandidates([
        {
          id: '1',
          name: 'John Doe',
          email: 'john.doe@email.com',
          job_title: 'Senior Software Developer',
          score: 85,
          status: 'shortlisted'
        },
        {
          id: '2',
          name: 'Jane Smith',
          email: 'jane.smith@email.com',
          job_title: 'Product Manager',
          score: 92,
          status: 'shortlisted'
        },
        {
          id: '3',
          name: 'Mike Johnson',
          email: 'mike.johnson@email.com',
          job_title: 'Data Analyst',
          score: 78,
          status: 'pending'
        }
      ])

      // Load interviews (mock data)
      setInterviews([
        {
          id: '1',
          candidate_name: 'John Doe',
          job_title: 'Senior Software Developer',
          date: '2024-01-15',
          time: '10:00',
          type: 'Technical',
          status: 'scheduled'
        },
        {
          id: '2',
          candidate_name: 'Jane Smith',
          job_title: 'Product Manager',
          date: '2024-01-16',
          time: '14:00',
          type: 'Behavioral',
          status: 'completed'
        }
      ])

      // Load email templates
      const templatesResponse = await rootAgentService.getEmailTemplates()
      setEmailTemplates(templatesResponse.templates || [])
    } catch (error) {
      console.error('Failed to load data:', error)
      toast({
        title: 'Error',
        description: 'Failed to load interview data',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleScheduleInterview = async () => {
    if (!selectedCandidate) return

    try {
      setScheduling(true)

      const candidateData = {
        name: selectedCandidate.name,
        email: selectedCandidate.email,
        phone: '', // Add missing required field
        position: selectedCandidate.job_title,
        experience: 0, // Add missing required field
        resume_score: selectedCandidate.score,
      }

      const interviewDetails = {
        date: interviewForm.interview_date,
        time: interviewForm.interview_time,
        duration: parseInt(interviewForm.duration),
        type: interviewForm.interview_type,
        interviewer: interviewForm.interviewer_name,
        location: interviewForm.location,
      }

      const response = await rootAgentService.scheduleInterview(candidateData, interviewDetails)

      if (response.success) {
        toast({
          title: 'Success',
          description: 'Interview scheduled successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        })

        // Add to interviews list
        const newInterview: Interview = {
          id: response.interview_id || Date.now().toString(),
          candidate_name: interviewForm.candidate_name,
          job_title: interviewForm.job_title,
          date: interviewForm.interview_date,
          time: interviewForm.interview_time,
          type: interviewForm.interview_type,
          status: 'scheduled'
        }

        setInterviews([...interviews, newInterview])
        onClose()
        resetForm()
      } else {
        throw new Error(response.message || 'Failed to schedule interview')
      }
    } catch (error) {
      console.error('Failed to schedule interview:', error)
      toast({
        title: 'Error',
        description: 'Failed to schedule interview',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setScheduling(false)
    }
  }

  const resetForm = () => {
    setInterviewForm({
      candidate_name: '',
      candidate_email: '',
      job_title: '',
      interview_date: '',
      interview_time: '',
      interview_type: '',
      interviewer_name: '',
      interviewer_email: '',
      location: '',
      duration: '60',
      notes: '',
      email_template: '',
    })
  }

  const openScheduleModal = (candidate: Candidate) => {
    setSelectedCandidate(candidate)
    setInterviewForm({
      ...interviewForm,
      candidate_name: candidate.name,
      candidate_email: candidate.email,
      job_title: candidate.job_title,
    })
    onOpen()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'shortlisted':
      case 'scheduled':
      case 'completed':
        return 'green'
      case 'pending':
        return 'yellow'
      default:
        return 'gray'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'green'
    if (score >= 60) return 'yellow'
    return 'red'
  }

  return (
    <MainLayout>
      <Box p={8}>
        {/* Header */}
        <VStack spacing={6} align="stretch" mb={8}>
          <Heading size="lg" color="gray.800">
            Interview Scheduler
          </Heading>
          
          <Text color="gray.600" fontSize="lg">
            Manage candidate interviews, schedule meetings, and send automated notifications.
          </Text>
        </VStack>

        <VStack spacing={8} align="stretch">
          {/* Stats Overview */}
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
            {[
              { label: 'Total Candidates', value: candidates.length, color: 'blue' },
              { label: 'Scheduled Interviews', value: interviews.filter(i => i.status === 'scheduled').length, color: 'green' },
              { label: 'Completed Interviews', value: interviews.filter(i => i.status === 'completed').length, color: 'purple' },
              { label: 'Pending Reviews', value: candidates.filter(c => c.status === 'pending').length, color: 'orange' },
            ].map((stat) => (
              <Card key={stat.label}>
                <CardBody>
                  <VStack spacing={2} align="center">
                    <Text fontSize="2xl" fontWeight="bold" color={`${stat.color}.500`}>
                      {stat.value}
                    </Text>
                    <Text fontSize="sm" color="gray.600" textAlign="center">
                      {stat.label}
                    </Text>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>

          {/* Candidates Section */}
          <Card>
            <CardBody>
              <VStack spacing={6} align="stretch">
                <Flex justify="space-between" align="center">
                  <Heading size="md" color="brand.500">Candidates</Heading>
                  <Button
                    leftIcon={<Icon as={Plus} />}
                    colorScheme="brand"
                    size="sm"
                  >
                    Add Candidate
                  </Button>
                </Flex>

                <TableContainer>
                  <Table>
                    <Thead>
                      <Tr>
                        <Th>Name</Th>
                        <Th>Job Title</Th>
                        <Th>Score</Th>
                        <Th>Status</Th>
                        <Th>Actions</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {candidates.map((candidate) => (
                        <Tr key={candidate.id}>
                          <Td>
                            <VStack align="start" spacing={1}>
                              <Text fontWeight="medium">{candidate.name}</Text>
                              <Text fontSize="sm" color="gray.600">{candidate.email}</Text>
                            </VStack>
                          </Td>
                          <Td>{candidate.job_title}</Td>
                          <Td>
                            <Badge colorScheme={getScoreColor(candidate.score)}>
                              {candidate.score}%
                            </Badge>
                          </Td>
                          <Td>
                            <Badge colorScheme={getStatusColor(candidate.status)}>
                              {candidate.status}
                            </Badge>
                          </Td>
                          <Td>
                            <HStack spacing={2}>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => openScheduleModal(candidate)}
                                isDisabled={candidate.status !== 'shortlisted'}
                              >
                                <Icon as={Calendar} boxSize={4} />
                              </Button>
                              <Button size="sm" variant="ghost">
                                <Icon as={Eye} boxSize={4} />
                              </Button>
                              <Button size="sm" variant="ghost">
                                <Icon as={Mail} boxSize={4} />
                              </Button>
                            </HStack>
                          </Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              </VStack>
            </CardBody>
          </Card>

          {/* Interviews Section */}
          <Card>
            <CardBody>
              <VStack spacing={6} align="stretch">
                <Heading size="md" color="brand.500">Scheduled Interviews</Heading>

                <TableContainer>
                  <Table>
                    <Thead>
                      <Tr>
                        <Th>Candidate</Th>
                        <Th>Job Title</Th>
                        <Th>Date & Time</Th>
                        <Th>Type</Th>
                        <Th>Status</Th>
                        <Th>Actions</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {interviews.map((interview) => (
                        <Tr key={interview.id}>
                          <Td>{interview.candidate_name}</Td>
                          <Td>{interview.job_title}</Td>
                          <Td>
                            <VStack align="start" spacing={1}>
                              <Text>{interview.date}</Text>
                              <Text fontSize="sm" color="gray.600">{interview.time}</Text>
                            </VStack>
                          </Td>
                          <Td>{interview.type}</Td>
                          <Td>
                            <Badge colorScheme={getStatusColor(interview.status)}>
                              {interview.status}
                            </Badge>
                          </Td>
                          <Td>
                            <HStack spacing={2}>
                              <Button size="sm" variant="ghost">
                                <Icon as={Eye} boxSize={4} />
                              </Button>
                              <Button size="sm" variant="ghost">
                                <Icon as={Edit} boxSize={4} />
                              </Button>
                              <Button size="sm" variant="ghost">
                                <Icon as={Send} boxSize={4} />
                              </Button>
                            </HStack>
                          </Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              </VStack>
            </CardBody>
          </Card>
        </VStack>

        {/* Schedule Interview Modal */}
        <Modal isOpen={isOpen} onClose={onClose} size="xl">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Schedule Interview</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={6} align="stretch">
                <SimpleGrid columns={2} spacing={4}>
                  <FormControl>
                    <FormLabel>Candidate Name</FormLabel>
                    <Input
                      value={interviewForm.candidate_name}
                      onChange={(e) => setInterviewForm({...interviewForm, candidate_name: e.target.value})}
                      isReadOnly
                    />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Candidate Email</FormLabel>
                    <Input
                      value={interviewForm.candidate_email}
                      onChange={(e) => setInterviewForm({...interviewForm, candidate_email: e.target.value})}
                      isReadOnly
                    />
                  </FormControl>
                </SimpleGrid>

                <FormControl>
                  <FormLabel>Job Title</FormLabel>
                  <Input
                    value={interviewForm.job_title}
                    onChange={(e) => setInterviewForm({...interviewForm, job_title: e.target.value})}
                    isReadOnly
                  />
                </FormControl>

                <SimpleGrid columns={2} spacing={4}>
                  <FormControl>
                    <FormLabel>Interview Date</FormLabel>
                    <Input
                      type="date"
                      value={interviewForm.interview_date}
                      onChange={(e) => setInterviewForm({...interviewForm, interview_date: e.target.value})}
                    />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Interview Time</FormLabel>
                    <Input
                      type="time"
                      value={interviewForm.interview_time}
                      onChange={(e) => setInterviewForm({...interviewForm, interview_time: e.target.value})}
                    />
                  </FormControl>
                </SimpleGrid>

                <SimpleGrid columns={2} spacing={4}>
                  <FormControl>
                    <FormLabel>Interview Type</FormLabel>
                    <Select
                      value={interviewForm.interview_type}
                      onChange={(e) => setInterviewForm({...interviewForm, interview_type: e.target.value})}
                      placeholder="Select type"
                    >
                      <option value="phone">Phone</option>
                      <option value="video">Video</option>
                      <option value="in-person">In-Person</option>
                      <option value="technical">Technical</option>
                      <option value="behavioral">Behavioral</option>
                    </Select>
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Duration (minutes)</FormLabel>
                    <Select
                      value={interviewForm.duration}
                      onChange={(e) => setInterviewForm({...interviewForm, duration: e.target.value})}
                    >
                      <option value="30">30 minutes</option>
                      <option value="60">60 minutes</option>
                      <option value="90">90 minutes</option>
                      <option value="120">120 minutes</option>
                    </Select>
                  </FormControl>
                </SimpleGrid>

                <SimpleGrid columns={2} spacing={4}>
                  <FormControl>
                    <FormLabel>Interviewer Name</FormLabel>
                    <Input
                      value={interviewForm.interviewer_name}
                      onChange={(e) => setInterviewForm({...interviewForm, interviewer_name: e.target.value})}
                      placeholder="Enter interviewer name"
                    />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Interviewer Email</FormLabel>
                    <Input
                      type="email"
                      value={interviewForm.interviewer_email}
                      onChange={(e) => setInterviewForm({...interviewForm, interviewer_email: e.target.value})}
                      placeholder="Enter interviewer email"
                    />
                  </FormControl>
                </SimpleGrid>

                <FormControl>
                  <FormLabel>Location/Meeting Link</FormLabel>
                  <Input
                    value={interviewForm.location}
                    onChange={(e) => setInterviewForm({...interviewForm, location: e.target.value})}
                    placeholder="Enter location or meeting link"
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Email Template</FormLabel>
                  <Select
                    value={interviewForm.email_template}
                    onChange={(e) => setInterviewForm({...interviewForm, email_template: e.target.value})}
                    placeholder="Select email template"
                  >
                    {emailTemplates.map((template) => (
                      <option key={template.template_id} value={template.template_id}>
                        {template.name}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>Notes</FormLabel>
                  <Textarea
                    value={interviewForm.notes}
                    onChange={(e) => setInterviewForm({...interviewForm, notes: e.target.value})}
                    placeholder="Additional notes for the interview"
                    rows={3}
                  />
                </FormControl>
              </VStack>
            </ModalBody>

            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onClose}>
                Cancel
              </Button>
              <Button
                colorScheme="brand"
                onClick={handleScheduleInterview}
                isLoading={scheduling}
                loadingText="Scheduling..."
              >
                Schedule Interview
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </Box>
    </MainLayout>
  )
}
