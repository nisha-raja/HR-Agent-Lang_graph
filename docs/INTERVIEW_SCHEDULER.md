# 📧 Interview Scheduling Agent

## Overview

The **Interview Scheduling Agent** is a sophisticated component of the HR Agent Suite that automatically processes candidate analysis results and sends appropriate emails based on their scores. It integrates with email services and calendar systems to streamline the interview process.

## Features

### 🎯 **Smart Candidate Processing**
- **Automatic Score Analysis**: Processes candidates based on their resume analysis scores
- **Threshold-Based Actions**: 
  - Scores ≥ 50: Automatically shortlisted for interview
  - Scores < 50: Rejection emails with constructive feedback
- **Override Capability**: HR can override recommendations for exceptional cases

### 📧 **Professional Email Templates**
- **Shortlisted Email Template**:
  - Congratulations message with score details
  - Interview scheduling information
  - Google Meet link generation
  - Preparation tips and requirements
  - Confirmation link for attendance

- **Rejection Email Template**:
  - Professional rejection notification
  - Score transparency
  - Constructive feedback and suggestions
  - Future opportunity encouragement
  - Contact information for questions

### 📅 **Interview Scheduling**
- **Automatic Date Calculation**: Schedules interviews for next business day
- **Google Meet Integration**: Generates unique meeting links
- **Confirmation System**: Provides confirmation links for candidates
- **Calendar Integration**: Ready for Google Calendar API integration

### 🎨 **Modern UI Design**
- **Responsive Interface**: Clean, professional design
- **Score Visualization**: Color-coded score displays
- **Candidate Management**: Sidebar navigation for multiple candidates
- **Email Preview**: Real-time email template preview
- **Status Tracking**: Visual status indicators for each candidate

## Installation & Setup

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Configure Email Settings**
Add the following to your `.env` file:

```env
# Email Configuration
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
COMPANY_NAME=Your Company Name
HR_EMAIL=hr@yourcompany.com

# Optional: Google Calendar Integration
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
```

### 3. **Gmail App Password Setup**
For Gmail, you'll need to create an App Password:

1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Create an App Password for "Mail"
4. Use this password in your `.env` file

## Usage

### **Running the Interview Scheduler**

#### Option 1: Standalone Application
```bash
python -m streamlit run ui/interview_scheduler_ui.py --server.port 8503
```

#### Option 2: Integrated with Main HR Suite
```bash
python -m streamlit run ui/hr_agent_ui.py --server.port 8501
```
Then navigate to "📧 Interview Scheduler" in the sidebar.

### **Workflow**

1. **Analyze Resumes**: Use the Resume Analyzer to score candidates
2. **Review Candidates**: View all analyzed candidates in the scheduler
3. **Select Candidate**: Choose a candidate from the sidebar
4. **Review Details**: Examine score breakdown and analysis
5. **Take Action**: Click appropriate action button:
   - **✅ SHORTLIST**: For scores ≥ 50 (or override)
   - **❌ REJECT**: For scores < 50 (or manual rejection)
6. **Email Sent**: Professional email automatically sent to candidate
7. **Interview Scheduled**: For shortlisted candidates (if applicable)

## Email Templates

### **Shortlisted Email Example**

**Subject**: Congratulations! You've Been Shortlisted for Software Engineer Position

**Content**:
- 🎉 Congratulations message
- 📊 Score display (e.g., "Your Analysis Score: 75/100")
- 📅 Interview details (date, time, format)
- 🎥 Google Meet link
- 📋 Preparation requirements
- ✅ Confirmation button
- 💡 Interview tips
- 📞 Contact information

### **Rejection Email Example**

**Subject**: Application Status - Software Engineer Position

**Content**:
- Professional rejection notification
- 📊 Score transparency
- 💡 Moving forward suggestions
- 🌟 Future opportunities
- 📞 Feedback request option
- Professional closing

## Configuration

### **Score Thresholds**
- **≥ 80**: Excellent Match - Highly Recommended
- **≥ 70**: Strong Candidate - Recommended  
- **≥ 50**: Shortlisted - Consider for Interview
- **≥ 30**: Consider for Other Roles
- **< 30**: Not Suitable for This Position

### **Customization Options**
- **Email Templates**: Modify templates in `interview_scheduler_agent.py`
- **Score Thresholds**: Adjust in the agent logic
- **Company Branding**: Update company name and contact details
- **Interview Scheduling**: Customize timing and format

## Technical Architecture

### **Core Components**

1. **InterviewSchedulerAgent** (`agents/interview_scheduler/interview_scheduler_agent.py`)
   - Main agent logic
   - Email template management
   - SMTP email sending
   - Interview scheduling

2. **Interview Scheduler UI** (`ui/interview_scheduler_ui.py`)
   - Streamlit-based interface
   - Candidate management
   - Email preview
   - Action buttons

3. **Root Agent Integration** (`agents/root_agent/hr_root_agent.py`)
   - Coordinates with other agents
   - Provides unified interface
   - Manages system status

### **Data Flow**
```
Resume Analysis → Analysis Results → Interview Scheduler → Email Processing → Calendar Integration
```

### **File Structure**
```
agents/
├── interview_scheduler/
│   ├── __init__.py
│   └── interview_scheduler_agent.py
ui/
├── interview_scheduler_ui.py
└── hr_agent_ui.py (integrated)
```

## API Integration

### **Email Services**
- **SMTP Support**: Gmail, Outlook, custom SMTP servers
- **HTML Templates**: Professional, responsive email design
- **Attachment Support**: Ready for resume attachments

### **Calendar Integration**
- **Google Calendar API**: Ready for integration
- **Meeting Link Generation**: Automatic Google Meet links
- **Event Creation**: Interview scheduling automation

### **Future Enhancements**
- **Zoom Integration**: Alternative video conferencing
- **Calendar Sync**: Two-way calendar synchronization
- **Email Tracking**: Delivery and read receipts
- **Template Customization**: Dynamic template builder

## Troubleshooting

### **Common Issues**

1. **Email Not Sending**
   - Check SMTP credentials in `.env`
   - Verify Gmail App Password
   - Test SMTP connection

2. **Template Errors**
   - Ensure all placeholders are filled
   - Check email template syntax
   - Verify candidate data format

3. **Calendar Integration**
   - Configure Google Calendar API
   - Set up proper authentication
   - Check calendar permissions

### **Debug Mode**
Enable debug logging by setting:
```env
DEBUG=true
```

## Security Considerations

- **Email Credentials**: Store securely in environment variables
- **Data Privacy**: Candidate information protection
- **Access Control**: Restrict to authorized HR personnel
- **Audit Trail**: Log all email actions for compliance

## Contributing

To extend the Interview Scheduling Agent:

1. **Add New Email Templates**: Modify template methods in the agent
2. **Integrate New Services**: Add calendar or email service providers
3. **Enhance UI**: Improve the Streamlit interface
4. **Add Analytics**: Track email effectiveness and candidate responses

## Support

For issues and questions:
- Check the troubleshooting section
- Review the main HR Agent Suite documentation
- Ensure all dependencies are properly installed
- Verify email configuration settings
