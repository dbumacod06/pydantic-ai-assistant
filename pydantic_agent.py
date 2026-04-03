from datetime import datetime, timedelta
import os
import uuid
from zoneinfo import ZoneInfo
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import smtplib
from email.message import EmailMessage


class MeetingDetails(BaseModel):
    recipientEmail: str
    title: str
    agenda: str
    meetingTime: datetime
    duration: int

class EmailDetails(BaseModel):
    recipientEmail: str
    subject: str
    content: str


SCOPES = ['https://www.googleapis.com/auth/calendar.events']
def getCalendarService() -> any:
    '''Initializes and returns the Google Calendar service object.'''
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('calendar', 'v3', credentials=creds)


service = getCalendarService()
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
smtpEmail = os.getenv('SMTP_EMAIL')
smtpAppKey = os.getenv('SMTP_APP_KEY')
if smtpEmail and smtpAppKey:
    server.login(smtpEmail, smtpAppKey)
else:
    print("Warning: SMTP_EMAIL or SMTP_APP_KEY not set.")

schedulerAgent = Agent(
    'openai:gpt-5.4-nano-2026-03-17',
    instructions=(
        "You are a virtual assistant for Dhoby, a software, data, and AI engineer."
        "You help Dhoby by setting up meetings and sending emails."
        "Use the provided tools to perform these actions."
        "If you don't have enough information to call a tool, ask the user for clarification."
    )
)


@schedulerAgent.system_prompt
def get_time_context() -> str:
    '''Provides the agent with the current date, time, and timezone context.'''
    now = datetime.now(ZoneInfo("Asia/Manila"))
    return f"The current time in the Philippines is {now.strftime('%A, %Y-%m-%d %H:%M:%S %Z')}. Assume this is the 'now' for all relative time requests unless stated otherwise."


@schedulerAgent.system_prompt
def get_meeting_context() -> str:
    '''Additional prompt when the user asks to schedule a meeting'''
    return f"""
    The user may have already provided some information, so check for the following information:
        1. The recipient's email address.
        2. The title of the meeting.
        3. The agenda of the meeting.
        4. The date and time of the meeting.
        5. The duration of the meeting.
    If the user only provided the title of the meeting, you can create a agenda for the user, and vice-versa.
    Once you have all the information, confirm the details with the user. If the user confirmed, call the setMeeting tool.
    """

@schedulerAgent.system_prompt
def get_email_context() -> str:
    '''Additional prompt when the user asks to send an email'''
    return f"""
    The user may have already provided some information, so check for the following information:
        1. The recipient's email address.   
        2. The subject of the email.
        3. The content of the email.
    If the user only provided the content of the email, you can create a subject for the user, and vice-versa.
    "When sending an email, make sure the content is professional, grateful, and includes Dhoby's signature: 'Best regards, Dhoby Bumacod'."
    Once you have all the information, confirm the details with the user. If the user confirmed, call the sendEmail tool.
    """


@schedulerAgent.tool
def setMeeting(ctx: RunContext[None], meetingDetails: MeetingDetails) -> str:
    '''Sets a meeting on Google Calendar and returns a success or failure message.'''
    try:
        startTime = meetingDetails.meetingTime
        durationToAdd = timedelta(minutes=meetingDetails.duration)
        event = {
                'summary': meetingDetails.title,
                'start': {'dateTime': startTime.replace(tzinfo=ZoneInfo("Asia/Manila")).isoformat()},
                'end': {'dateTime': (startTime + durationToAdd).replace(tzinfo=ZoneInfo("Asia/Manila")).isoformat()},
                'attendees': [
                    {'email': meetingDetails.recipientEmail}
                ],
                'conferenceData': {
                    'createRequest': {
                        'requestId': str(uuid.uuid4()),
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            }

        eventObj = service.events().insert(
            calendarId='primary', 
            body=event, 
            conferenceDataVersion=1
        ).execute()
        return f"Meeting successfully created! {meetingDetails}"
    except Exception as e:
        return f"Failed to set a meeting. Details: {meetingDetails}, Error: {e}"


@schedulerAgent.tool
def sendEmail(ctx: RunContext[None], emailDetails: EmailDetails) -> str:
    '''Sends an email via SMTP and returns a success or failure message.'''
    try:
        emailMsg = EmailMessage()
        emailMsg['Subject'] = emailDetails.subject
        emailMsg['From'] = os.getenv('SMTP_EMAIL')
        emailMsg['To'] = emailDetails.recipientEmail
        emailMsg.set_content(emailDetails.content)
        server.send_message(emailMsg)
        return f"Email successfully sent! {emailDetails}"
    except Exception as e:
        return f"Failed to send the email. Details: {emailDetails}, Error: {e}"



def main() -> None:
    '''Testing loop for the scheduler agent.'''
    while True:
        userInput = input("How can I help you today? \n")
        result = schedulerAgent.run_sync(userInput)
        print(result.output)
        

if __name__ == "__main__":
    main()