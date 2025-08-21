# MCP Google Calendar Integration Guide

## 🎯 **Current Status**
✅ **OAuth2 complexity removed** - No more credential setup issues  
✅ **MCP-ready code** - Interview scheduler is prepared for MCP integration  
✅ **Working fallback** - Generates Google Meet links without calendar integration  

## 🚀 **Next Steps for MCP Integration**

### **1. Set Up MCP Google Calendar Server**

When you have access to MCP Google Calendar tools, replace the `create_interview_event` method in `agents/interview_scheduler/interview_scheduler_agent.py`:

```python
def create_interview_event(self, candidate_name: str, job_title: str, interview_datetime: datetime, candidate_email: str) -> Dict[str, str]:
    """
    Create interview event using MCP Google Calendar
    """
    try:
        # MCP Google Calendar integration
        calendar_event = mcp_google_calendar.create_event(
            title=f"Interview: {candidate_name} - {job_title}",
            description=f"Interview with {candidate_name} for {job_title} position at {self.company_name}",
            start_time=interview_datetime,
            end_time=interview_datetime + timedelta(hours=1),
            attendees=[candidate_email, self.hr_email],
            location="Google Meet",
            reminders=[
                {"type": "email", "minutes": 24 * 60},  # 1 day before
                {"type": "popup", "minutes": 15}        # 15 minutes before
            ]
        )
        
        return {
            'event_id': calendar_event['id'],
            'meet_link': calendar_event['meet_link'],
            'calendar_link': calendar_event['calendar_link'],
            'success': True,
            'mcp_ready': True
        }
        
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return self._fallback_event_creation(candidate_name, job_title, interview_datetime)
```

### **2. Available MCP Functions (Expected)**

When MCP Google Calendar is configured, you should have access to:

```python
# Create calendar event
mcp_google_calendar.create_event(
    title="Event Title",
    description="Event Description", 
    start_time=datetime,
    end_time=datetime,
    attendees=["email1@example.com", "email2@example.com"],
    location="Location",
    reminders=[{"type": "email", "minutes": 1440}]
)

# Send reminders
mcp_google_calendar.send_reminder(
    event_id="event_id",
    message="Reminder message"
)

# Get calendar events
mcp_google_calendar.get_events(
    start_date=datetime,
    end_date=datetime
)
```

### **3. Testing MCP Integration**

Once MCP is set up, test the integration:

1. **Shortlist a candidate** in the Interview Scheduler
2. **Check if calendar event is created** in your Google Calendar
3. **Verify Google Meet link** is generated
4. **Confirm email is sent** with calendar details

## 🔧 **Current Working Features**

### **✅ What Works Now:**
- Interview scheduling logic
- Email templates (shortlisted/rejected)
- Google Meet link generation
- Candidate processing
- Score-based decisions

### **🔄 Ready for MCP:**
- Calendar event creation
- Real Google Meet integration
- Calendar invitations
- Reminder system

## 📋 **MCP Setup Commands**

When you have MCP access, use these commands:

```bash
# In Claude Code
/mcp add google-calendar https://server.smithery.ai/@goldk3y/google-calendar-mcp/mcp

# Or configure MCP server
/mcp configure google-calendar
```

## 🎉 **Benefits of MCP Integration**

1. **No OAuth2 setup** - Direct API access
2. **Simpler authentication** - MCP handles credentials
3. **Real calendar events** - Actual Google Calendar integration
4. **Automatic reminders** - Built-in notification system
5. **Consistent with existing MCP** - Same pattern as email integration

## 🚨 **Fallback Mode**

If MCP integration fails, the system will:
- Generate placeholder Google Meet links
- Continue sending emails
- Work without calendar integration
- Show `mcp_ready: false` flag

---

**Your HR Agent Suite is now MCP-ready! 🎯**
