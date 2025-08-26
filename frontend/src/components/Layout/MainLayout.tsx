'use client'

import { Box, Flex } from '@chakra-ui/react'
import Sidebar from './Sidebar'
import Header from './Header'
import AIChatBar from './AIChatBar'

interface MainLayoutProps {
  children: React.ReactNode
  onAIMessage?: (message: string) => void
}

export default function MainLayout({ children, onAIMessage }: MainLayoutProps) {
  const handleAIMessage = (message: string) => {
    if (onAIMessage) {
      onAIMessage(message)
    }
    // Default AI assistant behavior
    console.log('AI Assistant received:', message)
  }

  return (
    <Flex h="100vh" overflow="hidden">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content Area */}
      <Box flex={1} ml="280px" display="flex" flexDirection="column">
        {/* Header */}
        <Header />
        
        {/* Content */}
        <Box 
          flex={1} 
          overflow="auto" 
          pb="80px" // Account for AI chat bar
          bg="gray.50"
        >
          {children}
        </Box>
        
        {/* AI Chat Bar */}
        <AIChatBar onSendMessage={handleAIMessage} />
      </Box>
    </Flex>
  )
}
