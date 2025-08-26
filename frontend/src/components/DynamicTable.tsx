import React from 'react'
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Text,
  Badge,
  VStack,
  HStack,
  Icon,
  Heading,
  Divider
} from '@chakra-ui/react'
import { 
  Building, 
  Briefcase, 
  DollarSign, 
  Code, 
  Users,
  Info 
} from 'lucide-react'

interface DynamicTableProps {
  type: string
  message: string
  data: any
  query: string
  timestamp: string
}

const DynamicTable: React.FC<DynamicTableProps> = ({ 
  type, 
  message, 
  data, 
  query, 
  timestamp 
}) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'company_info': return Building
      case 'job_search': return Briefcase
      case 'salary_info': return DollarSign
      case 'skills_analysis': return Code
      case 'department_info': return Users
      default: return Info
    }
  }

  const getColorScheme = (type: string) => {
    switch (type) {
      case 'company_info': return 'blue'
      case 'job_search': return 'green'
      case 'salary_info': return 'purple'
      case 'skills_analysis': return 'orange'
      case 'department_info': return 'teal'
      default: return 'gray'
    }
  }

  const renderJobTable = () => {
    // Handle nested data structure
    const jobsArray = data.jobs?.jobs || data.jobs || []
    
    return (
      <TableContainer>
        <Table variant="simple" size="sm">
          <Thead>
            <Tr>
              <Th>Job Title</Th>
              <Th>Department</Th>
              <Th>Experience</Th>
              <Th>Salary Range</Th>
              <Th>Location</Th>
              <Th>Skills</Th>
            </Tr>
          </Thead>
          <Tbody>
            {jobsArray.map((job: any, index: number) => (
              <Tr key={index}>
                <Td fontWeight="medium">{job.job_title || 'N/A'}</Td>
                <Td>{job.department || 'N/A'}</Td>
                <Td>
                  {job.experience_level?.minimum && job.experience_level?.preferred 
                    ? `${job.experience_level.minimum}-${job.experience_level.preferred} years`
                    : 'Not specified'
                  }
                </Td>
                <Td>
                  {job.salary_range?.min && job.salary_range?.max
                    ? `${job.salary_range.min}-${job.salary_range.max} ${job.salary_range.currency || 'INR'}`
                    : 'Not specified'
                  }
                </Td>
                <Td>{job.locations?.join(', ') || 'Not specified'}</Td>
                <Td>
                  <HStack spacing={1} wrap="wrap">
                    {job.required_skills?.slice(0, 3).map((skill: string, i: number) => (
                      <Badge key={i} size="sm" colorScheme="blue">{skill}</Badge>
                    ))}
                    {job.required_skills?.length > 3 && (
                      <Badge size="sm" colorScheme="gray">+{job.required_skills.length - 3} more</Badge>
                    )}
                  </HStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </TableContainer>
    )
  }

  const renderSalaryTable = () => (
    <TableContainer>
      <Table variant="simple" size="sm">
        <Thead>
          <Tr>
            <Th>Job Title</Th>
            <Th>Department</Th>
            <Th>Experience Level</Th>
            <Th>Salary Range</Th>
          </Tr>
        </Thead>
        <Tbody>
          {data.salary_ranges?.map((salary: any, index: number) => (
            <Tr key={index}>
              <Td fontWeight="medium">{salary.job_title || 'N/A'}</Td>
              <Td>{salary.department || 'N/A'}</Td>
              <Td>{salary.experience_level || 'Not specified'}</Td>
              <Td fontWeight="bold" color="green.600">
                {salary.salary_range || 'Not specified'}
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  )

  const renderSkillsTable = () => (
    <TableContainer>
      <Table variant="simple" size="sm">
        <Thead>
          <Tr>
            <Th>Skill</Th>
            <Th>Job Count</Th>
            <Th>Category</Th>
          </Tr>
        </Thead>
        <Tbody>
          {data.skills?.map((skill: any, index: number) => (
            <Tr key={index}>
              <Td fontWeight="medium">{skill.name}</Td>
              <Td>
                <Badge colorScheme="blue">{skill.job_count}</Badge>
              </Td>
              <Td>{skill.category}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  )

  const renderDepartmentTable = () => (
    <TableContainer>
      <Table variant="simple" size="sm">
        <Thead>
          <Tr>
            <Th>Department</Th>
            <Th>Job Count</Th>
            <Th>Positions</Th>
          </Tr>
        </Thead>
        <Tbody>
          {data.departments?.map((dept: any, index: number) => (
            <Tr key={index}>
              <Td fontWeight="medium">{dept.name || 'N/A'}</Td>
              <Td>
                <Badge colorScheme="green">{dept.job_count || 0}</Badge>
              </Td>
              <Td>{dept.positions?.join(', ') || 'No positions'}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  )

  const renderCompanyInfo = () => (
    <Box p={4} bg="blue.50" borderRadius="lg">
      <VStack align="start" spacing={3}>
        <HStack>
          <Badge colorScheme="blue">{data.industry}</Badge>
          <Badge colorScheme="green">{data.size}</Badge>
        </HStack>
        <Text fontSize="lg" fontWeight="medium">{data.name}</Text>
        <Text color="gray.600">{data.about}</Text>
      </VStack>
    </Box>
  )

  const renderTable = () => {
    if (!data) {
      return <Text color="gray.500">No data available</Text>
    }

    try {
      switch (type) {
        case 'job_search':
          const jobsArray = data.jobs?.jobs || data.jobs || []
          return jobsArray.length > 0 ? renderJobTable() : <Text>No jobs found</Text>
        case 'salary_info':
          return data.salary_ranges?.length > 0 ? renderSalaryTable() : <Text>No salary data found</Text>
        case 'skills_analysis':
          return data.skills?.length > 0 ? renderSkillsTable() : <Text>No skills data found</Text>
        case 'department_info':
          return data.departments?.length > 0 ? renderDepartmentTable() : <Text>No department data found</Text>
        case 'company_info':
          return data.name ? renderCompanyInfo() : <Text>No company data found</Text>
        default:
          return <Text>Unknown data type</Text>
      }
    } catch (error) {
      console.error('Error rendering table:', error)
      return <Text color="red.500">Error displaying data</Text>
    }
  }

  return (
    <Box 
      border="1px" 
      borderColor="gray.200" 
      borderRadius="lg" 
      p={4} 
      mb={4}
      bg="white"
      shadow="sm"
    >
      <VStack align="start" spacing={3}>
        {/* Header */}
        <HStack spacing={3}>
          <Icon 
            as={getIcon(type)} 
            color={`${getColorScheme(type)}.500`}
            boxSize={5}
          />
          <Heading size="md" color={`${getColorScheme(type)}.500`}>
            {type.replace('_', ' ').toUpperCase()}
          </Heading>
          <Badge colorScheme={getColorScheme(type)}>
            {(() => {
              switch (type) {
                case 'job_search':
                  const jobsArray = data.jobs?.jobs || data.jobs || []
                  return `${jobsArray.length} items`
                case 'salary_info':
                  return `${data.salary_ranges?.length || 0} items`
                case 'skills_analysis':
                  return `${data.skills?.length || 0} items`
                case 'department_info':
                  return `${data.departments?.length || 0} items`
                default:
                  return `${data ? Object.keys(data).length : 0} items`
              }
            })()}
          </Badge>
        </HStack>

        <Divider />

        {/* Query Info */}
        <Box fontSize="sm" color="gray.600">
          <Text><strong>Query:</strong> {query}</Text>
          <Text><strong>Time:</strong> {timestamp}</Text>
        </Box>

        {/* Message */}
        <Text fontWeight="medium">{message}</Text>

        {/* Dynamic Table */}
        {renderTable()}
      </VStack>
    </Box>
  )
}

export default DynamicTable
