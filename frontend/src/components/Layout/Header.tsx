'use client'

import {
  Box,
  Flex,
  Text,
  Icon,
  Avatar,
  Badge,
  HStack,
  VStack,
} from '@chakra-ui/react'
import { 
  Search, 
  Mail, 
  Bell,
  ChevronRight
} from 'lucide-react'
import { usePathname } from 'next/navigation'

interface BreadcrumbItem {
  name: string
  path: string
  icon?: React.ComponentType<{ size?: number; className?: string }>
}

export default function Header() {
  const pathname = usePathname()

  // Generate breadcrumbs based on current path
  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    const segments = pathname.split('/').filter(Boolean)
    const breadcrumbs: BreadcrumbItem[] = [
      { name: 'PHOENIX_AI', path: '/' }
    ]

    if (segments.length === 0) {
      return breadcrumbs
    }

    // Map segments to readable names
    const segmentNames: { [key: string]: string } = {
      'people': 'People',
      'careers': 'Careers Hub',
      'analytics': 'Analytics',
      'pipeline': 'Pipeline',
      'jd': 'Job Description',
      'resume': 'Resume Analysis',
      'interview': 'Interview Scheduling',
    }

    let currentPath = ''
    segments.forEach((segment, index) => {
      currentPath += `/${segment}`
      const name = segmentNames[segment] || segment.charAt(0).toUpperCase() + segment.slice(1)
      breadcrumbs.push({
        name,
        path: currentPath,
      })
    })

    return breadcrumbs
  }

  const breadcrumbs = generateBreadcrumbs()

  return (
    <Box
      bg="white"
      borderBottom="1px"
      borderColor="gray.200"
      px={8}
      py={4}
      position="sticky"
      top={0}
      zIndex={5}
    >
      <Flex justify="space-between" align="center">
        {/* Breadcrumbs */}
        <HStack spacing={2}>
          {breadcrumbs.map((item, index) => (
            <HStack key={item.path} spacing={2}>
              {index > 0 && (
                <Icon as={ChevronRight} color="gray.400" boxSize={4} />
              )}
              <Text
                color={index === breadcrumbs.length - 1 ? 'brand.500' : 'gray.600'}
                fontWeight={index === breadcrumbs.length - 1 ? 'semibold' : 'medium'}
                fontSize="sm"
              >
                {item.name}
              </Text>
            </HStack>
          ))}
        </HStack>

        {/* Right side actions */}
        <HStack spacing={4}>
          {/* Search */}
          <Box
            as="button"
            p={2}
            borderRadius="md"
            _hover={{ bg: 'gray.100' }}
            transition="all 0.2s"
          >
            <Icon as={Search} color="gray.500" boxSize={5} />
          </Box>

          {/* Mail */}
          <Box
            as="button"
            p={2}
            borderRadius="md"
            _hover={{ bg: 'gray.100' }}
            transition="all 0.2s"
            position="relative"
          >
            <Icon as={Mail} color="gray.500" boxSize={5} />
          </Box>

          {/* Notifications */}
          <Box
            as="button"
            p={2}
            borderRadius="md"
            _hover={{ bg: 'gray.100' }}
            transition="all 0.2s"
            position="relative"
          >
            <Icon as={Bell} color="gray.500" boxSize={5} />
            <Badge
              position="absolute"
              top={1}
              right={1}
              colorScheme="red"
              borderRadius="full"
              fontSize="xs"
              minW="18px"
              h="18px"
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              3
            </Badge>
          </Box>

          {/* User Profile */}
          <HStack spacing={3}>
            <Avatar
              size="sm"
              name="Khadija"
              src="/api/placeholder/32/32"
              bg="brand.100"
              color="brand.600"
            />
            <VStack spacing={0} align="start">
              <Text fontSize="sm" fontWeight="medium" color="gray.800">
                Khadija
              </Text>
              <Text fontSize="xs" color="gray.500">
                AI Agent
              </Text>
            </VStack>
          </HStack>
        </HStack>
      </Flex>
    </Box>
  )
}
