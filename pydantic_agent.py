
from datetime import datetime, timedelta
import os
import uuid
from zoneinfo import ZoneInfo
from pydantic_ai import Agent
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import smtplib
from email.message import EmailMessage


class MeetingDetails(BaseModel):
    recipient_email: str
    title: str
    agenda: str
    meeting_time: datetime
    duration: int

class EmailDetails(BaseModel):
    recipient_email: str
    subject: str
    content: str


SCOPES = ['https://www.googleapis.com/auth/calendar.events']
def get_calendar_service():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('calendar', 'v3', credentials=creds)


service = get_calendar_service()
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(os.getenv('SMTP_EMAIL'),os.getenv('SMTP_APP_KEY'))

scheduler_agent = Agent(
    'openrouter:minimax/minimax-m2.5',
    output_type= EmailDetails | MeetingDetails | str,
    instructions=(
        "You are a virtual assistant for Dhoby, a software, data, and ai engineer."
        "A user can only ask you. to set up a meeting, send an email, paraphrasing or confirming an email or meeting."
        "If they want to set up a meeting, extract the recipient email, the title, agenda, time of the meeting, and the duration in minutes."
        "If they want to send an email, extract the email of the recipient, the subject. Extract the email content and modify it to make it professional and grateful and add an email signature from Dhoby Bumacod"
        "If you can't extract all data for either sending an email or setting up a meeting, ask the user to try again." 
        "Do not perform other tasks besides sending an email, setting up the meeting, paraphrasing or confirming an email or meeting."
    )
)


def set_meeting(meeting_details: MeetingDetails):
    try:
        start_time = meeting_details.meeting_time
        duration_to_add = timedelta(minutes=meeting_details.duration)
        event = {
                'summary': meeting_details.title,
                'start': {'dateTime': start_time.replace(tzinfo=ZoneInfo("Asia/Manila")).isoformat()},
                'end': {'dateTime': (start_time + duration_to_add).replace(tzinfo=ZoneInfo("Asia/Manila")).isoformat()},
                'attendees': [
                    {'email': meeting_details.recipient_email}
                ],
                'conferenceData': {
                    'createRequest': {
                        'requestId': str(uuid.uuid4()),
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            }

        event_obj = service.events().insert(
            calendarId='primary', 
            body=event, 
            conferenceDataVersion=1
        ).execute()
        return(f"Meeting succesfully created! {meeting_details}")
    except Exception as e:
        return f"Failed to set a meeting. Details as follows: {meeting_details}, {e}"



def send_email(email_details: EmailDetails):
    try:
        email_msg = EmailMessage()
        email_msg['Subject'] = email_details.subject
        email_msg['From'] = os.getenv('SMTP_EMAIL')
        email_msg['To'] = email_details.recipient_email
        email_msg.set_content(email_details.content)
        server.send_message(email_msg)
        return(f"Email successfuly sent! {email_details}")
    except Exception as e:
        return f"Failed to send the email. Details as follows: {email_details}, {e}"



def main():
    while True:
        user_input = input("How can I help you today? \n")
        result = scheduler_agent.run_sync(user_input)
        print(result.output)
        print(type(result.output))
        if isinstance(result.output,MeetingDetails):
            set_meeting(result.output)
            break
        if isinstance(result.output,EmailDetails):
            send_email(result.output)
            break
        

if __name__ == "__main__":
    main()