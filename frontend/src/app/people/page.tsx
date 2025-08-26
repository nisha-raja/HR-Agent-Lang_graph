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
  SimpleGrid,
  Icon,
  Badge,
  useToast,
} from '@chakra-ui/react'
import { 
  FileText, 
  Calendar,
  Upload,
  BarChart3,
  Settings
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import MainLayout from '@/components/Layout/MainLayout'
import { rootAgentService } from '@/services/api'

interface PeopleStats {
  totalCandidates: number
  activeJobs: number
  scheduledInterviews: number
  pendingReviews: number
}

export default function PeoplePage() {
  const [stats, setStats] = useState<PeopleStats>({
    totalCandidates: 0,
    activeJobs: 0,
    scheduledInterviews: 0,
    pendingReviews: 0,
  })
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const toast = useToast()

  const loadStats = async () => {
    try {
      setLoading(true)
      // Load job descriptions count
      const jdResponse = await rootAgentService.getJobDescriptions()
      const activeJobs = Array.isArray(jdResponse) ? jdResponse.length : (jdResponse.job_descriptions?.length || 0)
      
      // Load analysis history count
      const historyResponse = await rootAgentService.getAnalysisHistory()
      const totalCandidates = historyResponse.history?.length || 0
      
      setStats({
        totalCandidates,
        activeJobs,
        scheduledInterviews: Math.floor(Math.random() * 10) + 5, // Mock data
        pendingReviews: Math.floor(Math.random() * 20) + 10, // Mock data
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
      toast({
        title: 'Error',
        description: 'Failed to load people statistics',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStats()
  }, [loadStats])

  const peopleFunctions = [
    {
      title: 'Job Description Generator',
      description: 'Create and manage job descriptions with AI assistance',
      icon: FileText,
      color: 'brand.500',
      path: '/people/jd',
      stats: `${stats.activeJobs} active jobs`,
    },
    {
      title: 'Resume Analyzer',
      description: 'Upload and analyze candidate resumes against job requirements',
      icon: Upload,
      color: 'green.500',
      path: '/people/resume',
      stats: `${stats.totalCandidates} candidates analyzed`,
    },
    {
      title: 'Interview Scheduler',
      description: 'Schedule and manage candidate interviews',
      icon: Calendar,
      color: 'purple.500',
      path: '/people/interview',
      stats: `${stats.scheduledInterviews} interviews scheduled`,
    },
    {
      title: 'Candidate Analytics',
      description: 'View detailed analytics and reports on candidates',
      icon: BarChart3,
      color: 'orange.500',
      path: '/people/analytics',
      stats: `${stats.pendingReviews} pending reviews`,
    },
  ]

  return (
    <MainLayout>
      <Box p={8}>
        {/* Header */}
        <VStack spacing={6} align="stretch" mb={8}>
          <Heading size="lg" color="gray.800">
            People Management
          </Heading>
          
          <Text color="gray.600" fontSize="lg">
            Manage your HR processes with AI-powered tools for job descriptions, resume analysis, and interview scheduling.
          </Text>
        </VStack>

        {/* Stats Overview */}
        <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6} mb={8}>
          {[
            { label: 'Total Candidates', value: stats.totalCandidates, color: 'green' },
            { label: 'Active Jobs', value: stats.activeJobs, color: 'brand' },
            { label: 'Scheduled Interviews', value: stats.scheduledInterviews, color: 'purple' },
            { label: 'Pending Reviews', value: stats.pendingReviews, color: 'orange' },
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

        {/* HR Functions */}
        <VStack spacing={6} align="stretch">
          <Heading size="md" color="gray.800">
            HR Functions
          </Heading>
          
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
            {peopleFunctions.map((func) => (
              <Card 
                key={func.title}
                cursor="pointer"
                _hover={{ transform: 'translateY(-2px)', shadow: 'lg' }}
                transition="all 0.2s"
                onClick={() => router.push(func.path)}
              >
                <CardBody>
                  <VStack spacing={4} align="start">
                    <HStack spacing={3}>
                      <Box
                        p={2}
                        borderRadius="full"
                        bg={`${func.color}20`}
                        color={func.color}
                      >
                        <Icon as={func.icon} boxSize={6} />
                      </Box>
                      <VStack spacing={1} align="start">
                        <Text fontWeight="semibold" fontSize="lg">
                          {func.title}
                        </Text>
                        <Badge colorScheme={func.color.split('.')[0]} size="sm">
                          {func.stats}
                        </Badge>
                      </VStack>
                    </HStack>
                    
                    <Text fontSize="sm" color="gray.600">
                      {func.description}
                    </Text>
                    
                    <Button
                      size="sm"
                      colorScheme={func.color.split('.')[0]}
                      variant="outline"
                      rightIcon={<Icon as={func.icon} boxSize={4} />}
                    >
                      Open
                    </Button>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        </VStack>

        {/* Quick Actions */}
        <VStack spacing={6} align="stretch" mt={8}>
          <Heading size="md" color="gray.800">
            Quick Actions
          </Heading>
          
          <HStack spacing={4} flexWrap="wrap">
            <Button
              leftIcon={<Icon as={FileText} />}
              colorScheme="brand"
              onClick={() => router.push('/people/jd')}
            >
              Create New Job Description
            </Button>
            
            <Button
              leftIcon={<Icon as={Upload} />}
              colorScheme="green"
              onClick={() => router.push('/people/resume')}
            >
              Upload Resume
            </Button>
            
            <Button
              leftIcon={<Icon as={Calendar} />}
              colorScheme="purple"
              onClick={() => router.push('/people/interview')}
            >
              Schedule Interview
            </Button>
            
            <Button
              leftIcon={<Icon as={Settings} />}
              variant="outline"
            >
              Settings
            </Button>
          </HStack>
        </VStack>
      </Box>
    </MainLayout>
  )
}
