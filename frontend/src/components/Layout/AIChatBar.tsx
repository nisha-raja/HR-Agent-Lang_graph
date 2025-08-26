'use client'

import {
  Box,
  Input,
  Icon,
  HStack,
  IconButton,
  useColorModeValue,
} from '@chakra-ui/react'
import { 
  Search, 
  Mic, 
  Camera, 
  X,
  Zap
} from 'lucide-react'
import { useState } from 'react'

interface AIChatBarProps {
  onSendMessage: (message: string) => void
  placeholder?: string
}

export default function AIChatBar({ 
  onSendMessage, 
  placeholder = "Type here..." 
}: AIChatBarProps) {
  const [message, setMessage] = useState('')
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message.trim())
      setMessage('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleClear = () => {
    setMessage('')
  }

  return (
    <Box
      position="fixed"
      bottom={0}
      left="280px" // Account for sidebar width
      right={0}
      bg={bgColor}
      borderTop="1px"
      borderColor={borderColor}
      p={4}
      zIndex={10}
    >
      <HStack spacing={3} maxW="4xl" mx="auto">
        {/* Search Icon */}
        <Icon as={Search} color="gray.400" boxSize={5} />

        {/* Input Field */}
        <Input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          border="none"
          bg="transparent"
          _focus={{
            outline: 'none',
            boxShadow: 'none',
          }}
          _placeholder={{
            color: 'gray.400',
          }}
          flex={1}
        />

        {/* Action Icons */}
        <HStack spacing={2}>
          {message && (
            <IconButton
              aria-label="Clear message"
              icon={<Icon as={X} />}
              size="sm"
              variant="ghost"
              color="gray.400"
              _hover={{ color: 'gray.600' }}
              onClick={handleClear}
            />
          )}
          
          <IconButton
            aria-label="Voice input"
            icon={<Icon as={Mic} />}
            size="sm"
            variant="ghost"
            color="gray.400"
            _hover={{ color: 'gray.600' }}
          />
          
          <IconButton
            aria-label="Camera input"
            icon={<Icon as={Camera} />}
            size="sm"
            variant="ghost"
            color="gray.400"
            _hover={{ color: 'gray.600' }}
          />
          
          <IconButton
            aria-label="Send message"
            icon={<Icon as={Zap} />}
            size="sm"
            colorScheme="brand"
            borderRadius="full"
            onClick={handleSend}
            isDisabled={!message.trim()}
          />
        </HStack>
      </HStack>
    </Box>
  )
}
