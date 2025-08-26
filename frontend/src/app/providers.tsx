'use client'

import { ChakraProvider, extendTheme } from '@chakra-ui/react'

// Custom theme matching PHOENIX AI design
const theme = extendTheme({
  colors: {
    brand: {
      50: '#E6F3FF',
      100: '#B3D9FF',
      200: '#80BFFF',
      300: '#4DA6FF',
      400: '#1A8CFF',
      500: '#0073E6', // Primary blue
      600: '#005BB3',
      700: '#004280',
      800: '#002A4D',
      900: '#00111A',
    },
    sidebar: {
      500: '#1E3A8A', // Dark blue for sidebar
      600: '#1E40AF',
      700: '#1E3A8A',
    },
    gray: {
      50: '#F9FAFB',
      100: '#F3F4F6',
      200: '#E5E7EB',
      300: '#D1D5DB',
      400: '#9CA3AF',
      500: '#6B7280',
      600: '#4B5563',
      700: '#374151',
      800: '#1F2937',
      900: '#111827',
    }
  },
  fonts: {
    heading: 'Inter, system-ui, sans-serif',
    body: 'Inter, system-ui, sans-serif',
  },
  components: {
    Button: {
      defaultProps: {
        colorScheme: 'brand',
      },
    },
  },
  styles: {
    global: {
      body: {
        bg: 'white',
        color: 'gray.800',
      },
    },
  },
})

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ChakraProvider theme={theme}>
      {children}
    </ChakraProvider>
  )
}
