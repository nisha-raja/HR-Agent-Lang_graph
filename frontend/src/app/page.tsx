'use client'

import {
  Box,
  Grid,
  Card,
  CardBody,
  Text,
  Heading,
  VStack,
  HStack,
  Icon,
  Badge,
  useToast,
  Spinner,
  SimpleGrid,
} from '@chakra-ui/react'
import { 
  FileText, 
  Users, 
  Calendar,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Clock,
  Zap
} from 'lucide-react'
import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import MainLayout from '@/components/Layout/MainLayout'
import { rootAgentService, apiUtils } from '@/services/api'

interface SystemStatus {
  status: string
  agents: {
    jd_generator: string
    resume_analyzer: string
    interview_scheduler: string
  }
  message: string
}

export default function Dashboard() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [aiQuery, setAiQuery] = useState('')
  const router = useRouter()
  const toast = useToast()

  const loadSystemStatus = useCallback(async () => {
    try {
      setLoading(true)
      const status = await rootAgentService.getHealth()
      setSystemStatus(status)
    } catch (error) {
      console.error('Failed to load system status:', error)
      toast({
        title: 'Error',
        description: 'Failed to load system status',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }, [toast])

  useEffect(() => {
    loadSystemStatus()
  }, [loadSystemStatus])

  const handleAIMessage = async (message: string) => {
    try {
      setAiQuery(message)
      
      // Use AI assistant for parsing and routing
      const response = await rootAgentService.aiAssistant(message)
      
      if (response.action === 'parse_and_generate_job_description' && response.parsed_data) {
        // Navigate to JD Generator with pre-filled data
        router.push(`/people/jd?data=${encodeURIComponent(JSON.stringify(response.parsed_data))}`)
        toast({
          title: 'AI Assistant',
          description: response.message,
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
      } else if (response.action === 'validation_required' || !response.success) {
        // Show validation issues to user
        const issues = response.validation_issues || []
        const suggestions = response.suggestions || []
        
        let description = response.message + '\n\n'
        if (issues.length > 0) {
          description += 'Issues:\n' + issues.map((issue: string, index: number) => `${index + 1}. ${issue}`).join('\n')
        }
        if (suggestions.length > 0) {
          description += '\n\nSuggestions:\n' + suggestions.map((suggestion: string, index: number) => `${index + 1}. ${suggestion}`).join('\n')
        }
        
        toast({
          title: response.action === 'validation_required' ? 'Validation Required' : 'Processing Error',
          description: description,
          status: 'warning',
          duration: 10000,
          isClosable: true,
        })
      } else {
        // Handle other AI assistant responses
        toast({
          title: 'AI Assistant',
          description: response.message,
          status: 'info',
          duration: 3000,
          isClosable: true,
        })
      }
    } catch (error) {
      console.error('AI Assistant error:', error)
      toast({
        title: 'Error',
        description: 'Failed to process AI request',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'green'
      case 'error':
        return 'red'
      default:
        return 'yellow'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return CheckCircle
      case 'error':
        return AlertCircle
      default:
        return Clock
    }
  }

  const quickActions = [
    {
      title: 'Create Job Description',
      description: 'Generate a new job description',
      icon: FileText,
      color: 'brand.500',
      path: '/people/jd',
    },
    {
      title: 'Analyze Resume',
      description: 'Upload and analyze candidate resumes',
      icon: Users,
      color: 'green.500',
      path: '/people/resume',
    },
    {
      title: 'Schedule Interview',
      description: 'Manage interview scheduling',
      icon: Calendar,
      color: 'purple.500',
      path: '/people/interview',
    },
    {
      title: 'View Analytics',
      description: 'Check system performance and metrics',
      icon: TrendingUp,
      color: 'orange.500',
      path: '/analytics',
    },
  ]

  if (loading) {
    return (
      <MainLayout onAIMessage={handleAIMessage}>
        <Box display="flex" justifyContent="center" alignItems="center" h="full">
          <VStack spacing={4}>
            <Spinner size="xl" color="brand.500" />
            <Text>Loading system status...</Text>
          </VStack>
        </Box>
      </MainLayout>
    )
  }

  return (
    <MainLayout onAIMessage={handleAIMessage}>
      <Box p={8}>
        {/* Header */}
        <VStack spacing={6} align="stretch" mb={8}>
          <Heading size="lg" color="gray.800">
            Dashboard
          </Heading>
          
          {/* System Status */}
          {systemStatus && (
            <Card>
              <CardBody>
                <HStack justify="space-between" align="center">
                  <VStack align="start" spacing={2}>
                    <HStack>
                      <Icon 
                        as={getStatusIcon(systemStatus.status)} 
                        color={`${getStatusColor(systemStatus.status)}.500`}
                        boxSize={5}
                      />
                      <Text fontWeight="semibold">System Status</Text>
                    </HStack>
                    <Text color="gray.600" fontSize="sm">
                      {systemStatus.message}
                    </Text>
                  </VStack>
                  <Badge 
                    colorScheme={getStatusColor(systemStatus.status)}
                    fontSize="sm"
                    px={3}
                    py={1}
                  >
                    {systemStatus.status.toUpperCase()}
                  </Badge>
                </HStack>
              </CardBody>
            </Card>
          )}
        </VStack>

        {/* Agent Status Grid */}
        <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={6} mb={8}>
          {systemStatus && Object.entries(systemStatus.agents).map(([agent, status]) => (
            <Card key={agent}>
              <CardBody>
                <VStack align="start" spacing={3}>
                  <HStack justify="space-between" w="full">
                    <Text fontWeight="semibold" textTransform="capitalize">
                      {agent.replace('_', ' ')}
                    </Text>
                    <Badge 
                      colorScheme={getStatusColor(status)}
                      fontSize="xs"
                    >
                      {status}
                    </Badge>
                  </HStack>
                  <HStack>
                    <Icon 
                      as={getStatusIcon(status)} 
                      color={`${getStatusColor(status)}.500`}
                      boxSize={4}
                    />
                    <Text fontSize="sm" color="gray.600">
                      {status === 'healthy' ? 'Operational' : 'Issues detected'}
                    </Text>
                  </HStack>
                </VStack>
              </CardBody>
            </Card>
          ))}
        </Grid>

        {/* Quick Actions */}
        <VStack spacing={6} align="stretch">
          <Heading size="md" color="gray.800">
            Quick Actions
          </Heading>
          
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            {quickActions.map((action) => (
              <Card 
                key={action.title}
                cursor="pointer"
                _hover={{ transform: 'translateY(-2px)', shadow: 'lg' }}
                transition="all 0.2s"
                onClick={() => router.push(action.path)}
              >
                <CardBody>
                  <VStack spacing={4} align="center">
                    <Box
                      p={3}
                      borderRadius="full"
                      bg={`${action.color}20`}
                      color={action.color}
                    >
                      <Icon as={action.icon} boxSize={6} />
                    </Box>
                    <VStack spacing={2} align="center">
                      <Text fontWeight="semibold" textAlign="center">
                        {action.title}
                      </Text>
                      <Text fontSize="sm" color="gray.600" textAlign="center">
                        {action.description}
                      </Text>
                    </VStack>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        </VStack>

        {/* AI Assistant Demo */}
        {aiQuery && (
          <Box mt={8} p={4} bg="brand.50" borderRadius="lg" border="1px" borderColor="brand.200">
            <VStack spacing={3} align="start">
              <HStack>
                <Icon as={Zap} color="brand.500" boxSize={5} />
                <Text fontWeight="semibold" color="brand.700">
                  AI Assistant Response
                </Text>
              </HStack>
              <Text fontSize="sm" color="gray.700">
                Query: &ldquo;{aiQuery}&rdquo;
              </Text>
              <Text fontSize="sm" color="gray.600">
                Processing your request...
              </Text>
            </VStack>
          </Box>
        )}
      </Box>
    </MainLayout>
  )
}
