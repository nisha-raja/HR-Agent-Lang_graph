# PHOENIX AI - HR Agent Suite Frontend

A modern React-based frontend for the HR Agent Suite, built with Next.js and Chakra UI.

## 🚀 Features

- **Modern UI Design**: Clean, professional interface matching the PHOENIX AI brand
- **AI Assistant Integration**: Smart chat bar for natural language interactions
- **Modular Architecture**: Plug-and-play agent integration
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Updates**: Live status monitoring and data synchronization

## 🏗️ Architecture

### Components Structure
```
src/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Dashboard
│   ├── people/            # HR functions
│   │   ├── page.tsx       # People overview
│   │   ├── jd/           # Job Description Generator
│   │   ├── resume/       # Resume Analyzer
│   │   └── interview/    # Interview Scheduler
│   └── layout.tsx        # Root layout
├── components/            # Reusable components
│   └── Layout/           # Layout components
│       ├── MainLayout.tsx
│       ├── Sidebar.tsx
│       ├── Header.tsx
│       └── AIChatBar.tsx
└── services/             # API services
    └── api.ts           # Agent communication
```

### Agent Integration
- **Root Agent Gateway**: Central routing and coordination
- **JD Generator Agent**: Job description creation and management
- **Resume Analyzer Agent**: Resume analysis and scoring
- **Interview Scheduler Agent**: Interview scheduling and management

## 🛠️ Technology Stack

- **Framework**: Next.js 15 with App Router
- **UI Library**: Chakra UI
- **Icons**: Lucide React
- **Forms**: React Hook Form with Zod validation
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS + Chakra UI
- **TypeScript**: Full type safety

## 📦 Installation

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Environment Setup**:
   Create a `.env.local` file in the frontend directory:
   ```env
   NEXT_PUBLIC_ROOT_AGENT_URL=http://localhost:8000
   NEXT_PUBLIC_JD_GENERATOR_URL=http://localhost:8001
   NEXT_PUBLIC_RESUME_ANALYZER_URL=http://localhost:8002
   NEXT_PUBLIC_INTERVIEW_SCHEDULER_URL=http://localhost:8003
   ```

3. **Start Development Server**:
   ```bash
   npm run dev
   ```

4. **Build for Production**:
   ```bash
   npm run build
   npm start
   ```

## 🎯 Usage

### Dashboard
- View system status and agent health
- Quick access to all HR functions
- AI assistant integration

### Job Description Generator
- Multi-step form for creating job descriptions
- AI-powered content generation
- Template management and publishing

### Resume Analyzer
- File upload for resume analysis
- AI-powered scoring and insights
- Skills matching and recommendations

### Interview Scheduler
- Candidate management
- Interview scheduling with calendar integration
- Email template management

### AI Assistant
- Natural language queries
- Automatic routing to appropriate agents
- Context-aware responses

## 🔧 Configuration

### Theme Customization
The app uses a custom Chakra UI theme defined in `src/app/providers.tsx`:

```typescript
const theme = extendTheme({
  colors: {
    brand: {
      500: '#0073E6', // Primary blue
      // ... other shades
    },
    sidebar: {
      500: '#1E3A8A', // Dark blue for sidebar
    }
  }
})
```

### API Configuration
API endpoints are configured in `src/services/api.ts`:

```typescript
const ROOT_AGENT_URL = 'http://localhost:8000'
const JD_GENERATOR_URL = 'http://localhost:8001'
const RESUME_ANALYZER_URL = 'http://localhost:8002'
const INTERVIEW_SCHEDULER_URL = 'http://localhost:8003'
```

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Manual Deployment
1. Build the application: `npm run build`
2. Start the production server: `npm start`
3. Configure reverse proxy (nginx/Apache) if needed

## 🔌 API Integration

### Root Agent Communication
```typescript
import { rootAgentService } from '@/services/api'

// Health check
const health = await rootAgentService.getHealth()

// AI Assistant
const response = await rootAgentService.aiAssistant("Create a job description for a React developer")

// Generate job description
const jd = await rootAgentService.generateJobDescription(jobDetails)
```

### Direct Agent Communication
```typescript
import { jdGeneratorService, resumeAnalyzerService, interviewSchedulerService } from '@/services/api'

// Direct JD Generator
const result = await jdGeneratorService.generate(jobDetails)

// Direct Resume Analysis
const analysis = await resumeAnalyzerService.analyze(resumeData, jobDescriptionData)

// Direct Interview Scheduling
const interview = await interviewSchedulerService.schedule(candidateData, interviewDetails)
```

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### E2E Tests
```bash
npm run test:e2e
```

### Component Testing
```bash
npm run test:components
```

## 📱 Responsive Design

The application is fully responsive with breakpoints:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## 🔒 Security

- CORS configuration for API communication
- Input validation and sanitization
- Secure environment variable handling
- HTTPS enforcement in production

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Kill process on port 3000
   npx kill-port 3000
   ```

2. **API Connection Issues**:
   - Verify all agent services are running
   - Check environment variables
   - Ensure CORS is properly configured

3. **Build Errors**:
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules .next
   npm install
   ```

## 📈 Performance

- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js built-in optimization
- **Caching**: Static generation and ISR
- **Bundle Analysis**: `npm run analyze`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Contact the development team

---

**Built with ❤️ by the PHOENIX AI Team**
