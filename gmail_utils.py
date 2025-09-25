
import base64
import os.path
import datetime
import mimetypes
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage
from email.utils import make_msgid
from email.charset import Charset
import pytz

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/calendar.events.owned"
    ]

def send_email(subject, message, attachments, to):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        #Create Message
        message_text = MIMEText(message, 'text')
        message_html = MIMEText(message, 'html')
        mime_message = EmailMessage()
        mime_message.set_charset(Charset('utf-8'))
        mime_message.set_content(message_html)
        #mime_message.add_alternative(message_html)
        mime_message["To"] = to
        mime_message["From"] = "inovacaoead@unifil.br"
        mime_message["Subject"] = subject
        # Add Attachment# attachment
        # guessing the MIME type
        if attachments != None:
            attachment_filename = "Unifil1.jpg"
            type_subtype, _ = mimetypes.guess_type(attachment_filename)
            maintype, subtype = type_subtype.split("/")
            with open(attachment_filename, "rb") as fp:
                attachment_data = fp.read()
            mime_message.add_attachment(attachment_data, maintype, subtype)
        # encoded message
        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (service
                        .users()
                        .messages()
                        .send(userId='me',body=create_message)
                        .execute())
        print(f'Message Id: {send_message["id"]}')
        return "Ok"

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")
        return "Error"
    
def define_student_email(date,time,comprovante):
    
    html = open("templates/student_email.html", encoding='utf-8').read()
    #print(html)
    html = date.join(html.split("-date-"))
    html = time.join(html.split("-time-"))
    html = comprovante.join(html.split("-comprovante-"))
    return html   

def define_teacher_email(date,time,name,email):
    
    html = open("templates/teacher_email.html", encoding='utf-8').read()
    #print(html)
    html = date.join(html.split("-date-"))
    html = time.join(html.split("-time-"))
    html = name.join(html.split("-name-"))
    html = email.join(html.split("-email-"))
    return html

def create_calendar(date_time,invitee):
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)
    br_time = pytz.timezone('Brazil/East')
    date_time = datetime.datetime.fromisoformat(date_time+"-03:00")
    # Call the Calendar API
    start = date_time
    end = start + datetime.timedelta(minutes=30)
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .insert(
            calendarId="c_fa9b5b7d5c8cab8cd42440a81b4b6c0b3bee9c27d2a9c56f0379832f5acca336@group.calendar.google.com",
            body={
               'summary' : "Tour Gastronomia",
               'start' : {
                    'dateTime' : start.isoformat()
                    },
               'end' : {
                    'dateTime' : end.isoformat()
                        },
               'attendees': [
                  {
                     'email':invitee,
                     'responseStatus':'needsAction'
                  },
                  {
                     'email':'gastronomia@unifil.br',
                     'responseStatus':'needsAction'
                  }
               ]
               }
        )
        .execute()
    )
    print(events_result)


  except HttpError as error:
    print(f"An error occurred: {error}")