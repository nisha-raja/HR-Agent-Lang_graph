'use client'

import {
  Box,
  VStack,
  Text,
  Icon,
  Flex,
  useColorModeValue,
} from '@chakra-ui/react'
import { 
  Home, 
  Users, 
  TrendingUp, 
  BarChart3, 
  Link,
  Zap
} from 'lucide-react'
import { useRouter, usePathname } from 'next/navigation'

interface NavItem {
  name: string
  icon: React.ComponentType<{ size?: number; className?: string }>
  path: string
}

const navItems: NavItem[] = [
  { name: 'Dashboard', icon: Home, path: '/' },
  { name: 'People', icon: Users, path: '/people' },
  { name: 'Careers Hub', icon: TrendingUp, path: '/careers' },
  { name: 'Analytics', icon: BarChart3, path: '/analytics' },
  { name: 'Pipeline', icon: Link, path: '/pipeline' },
]

export default function Sidebar() {
  const router = useRouter()
  const pathname = usePathname()
  const bgColor = useColorModeValue('sidebar.500', 'sidebar.600')

  return (
    <Box
      bg={bgColor}
      w="280px"
      h="100vh"
      position="fixed"
      left={0}
      top={0}
      zIndex={10}
      boxShadow="lg"
    >
      <VStack spacing={8} align="stretch" h="full" p={6}>
        {/* Logo */}
        <Flex align="center" justify="center" py={4}>
          <Flex align="center" gap={2}>
            <Icon as={Zap} color="white" boxSize={8} />
            <Text
              fontSize="2xl"
              fontWeight="bold"
              color="white"
              letterSpacing="tight"
            >
              PHOENIX AI
            </Text>
            <Text
              fontSize="sm"
              color="brand.200"
              fontWeight="medium"
            >
              AI
            </Text>
          </Flex>
        </Flex>

        {/* Navigation Items */}
        <VStack spacing={2} align="stretch" flex={1}>
          {navItems.map((item) => {
            const isActive = pathname === item.path
            return (
              <Box
                key={item.name}
                as="button"
                w="full"
                p={3}
                borderRadius="lg"
                bg={isActive ? 'whiteAlpha.200' : 'transparent'}
                color={isActive ? 'white' : 'whiteAlpha.800'}
                _hover={{
                  bg: 'whiteAlpha.100',
                  color: 'white',
                }}
                transition="all 0.2s"
                onClick={() => router.push(item.path)}
                position="relative"
              >
                {isActive && (
                  <Box
                    position="absolute"
                    left={0}
                    top="50%"
                    transform="translateY(-50%)"
                    w={1}
                    h={8}
                    bg="brand.300"
                    borderRadius="full"
                  />
                )}
                <Flex align="center" gap={3}>
                  <Icon as={item.icon} boxSize={5} />
                  <Text fontWeight="medium">{item.name}</Text>
                </Flex>
              </Box>
            )
          })}
        </VStack>

        {/* Bottom Decoration */}
        <Box
          position="absolute"
          bottom={4}
          left="50%"
          transform="translateX(-50%)"
          opacity={0.3}
        >
          <Box
            w="60px"
            h="60px"
            borderRadius="full"
            bg="brand.300"
            filter="blur(20px)"
          />
        </Box>
      </VStack>
    </Box>
  )
}
