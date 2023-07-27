import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from typing import Optional

from parser import create_json

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# event = {
#   'summary': 'Google I/O 2015',
#   'location': '800 Howard St., San Francisco, CA 94103',
#   'description': 'A chance to hear more about Google\'s developer products.',
#   'start': {
#     'dateTime': '2015-05-28T09:00:00-07:00',
#     'timeZone': 'America/Los_Angeles',
#   },
#   'end': {
#     'dateTime': '2015-05-28T17:00:00-07:00',
#     'timeZone': 'America/Los_Angeles',
#   },
#   'recurrence': [
#     'RRULE:FREQ=DAILY;COUNT=2'
#   ],
#   'attendees': [
#     {'email': 'lpage@example.com'},
#     {'email': 'sbrin@example.com'},
#   ],
#   'reminders': {
#     'useDefault': False,
#     'overrides': [
#       {'method': 'email', 'minutes': 24 * 60},
#       {'method': 'popup', 'minutes': 10},
#     ],
#   },
# }

class Event(BaseModel):
    summary: str = Field(description="title of the event", example='Meeting with John')
    location: Optional[str] = Field(description="where the event is, or the location of the event", 
                                    example="800 Howard St., San Francisco, CA 94103")
    description: Optional[str] = Field(description="What the event is about", 
                                        example="Discussing the new project")
    start_time: str = Field(description="The start time of the event, in datetime format", 
                            example="2021-10-10T09:00:00-07:00")
    end_time: str = Field(description="The end time of the event, in datetime format, if not specified set to an hour later than start time", 
                            example="2021-10-10T10:00:00-07:00")
    recurrence: Optional[str] = Field(description="How often is the meeting happening", 
                                        example="RRULE:FREQ=DAILY;COUNT=2")
    email1: Optional[str] = Field(description="The email of another person sharing the invite", 
                                    example="kadija@")
    email2: str = Field (description="Another email that is being used to share with this person", 
                        example="kadija@")
    reminders: dict = Field(description="How often you want to be reminded of the event", 
                            example="{'useDefault': False, 'overrides': [{'method': 'email', 'minutes': 24 * 60}, {'method': 'popup', 'minutes': 10}]}")

def create_event(event_json):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        event = service.events().insert(calendarId='primary', body=event_json).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        return 1

    except HttpError as error:
        print('An error occurred: %s' % error)
        return 0 

if __name__ == '__main__':
    event_j = create_json("Create a calendar event for tomorrow at 3pm", Event)
    create_event(event_j)