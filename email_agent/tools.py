import base64
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional

from secret_utils import get_google_credentials, get_gmail_token

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    """Builds and returns the Gmail API service."""
    creds = get_gmail_token()
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh Gmail token: {e}")
                creds = None
        
        # If we still don't have valid creds (either didn't have them or refresh failed)
        if not creds or not creds.valid:
            creds_json = get_google_credentials()
            if not creds_json:
                raise FileNotFoundError("Gmail credentials not found. Please provide 'credentials.json' or set GOOGLE_CREDENTIALS_JSON environment variable.")
            
            # Note: run_local_server is fine for local dev but will fail in headless production.
            # In production, GMAIL_TOKEN_PICKLE should already be set in the environment.
            if os.getenv('KUBERNETES_SERVICE_HOST'):
                 raise RuntimeError("Interactive auth flow is disabled in production. Please provide GMAIL_TOKEN_PICKLE.")

            flow = InstalledAppFlow.from_client_config(creds_json, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Save the credentials locally if we are in dev
            token_path = 'token.pickle'
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)


    service = build('gmail', 'v1', credentials=creds)
    return service

def send_gmail_message(to: str, subject: str, body: str) -> str:
    """Sends an email message.
    
    Args:
        to: The email address of the recipient.
        subject: The subject of the email.
        body: The plain text body of the email.
    """
    try:
        service = get_gmail_service()
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId='me', body={'raw': raw}).execute()
        return f"Email sent successfully to {to} with subject '{subject}'"
    except Exception as e:
        return f"Error sending email: {str(e)}"

def search_gmail_messages(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Searches for emails matching the query.
    
    Args:
        query: The Gmail search query (e.g., 'from:someone@example.com', 'subject:report').
        max_results: The maximum number of results to return.
    """
    try:
        service = get_gmail_service()
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        detailed_messages = []
        for msg in messages:
            # We get minimal format first to avoid excessive data, but enough for a list
            m = service.users().messages().get(userId='me', id=msg['id'], format='minimal').execute()
            detailed_messages.append({
                'id': m['id'],
                'threadId': m['threadId'],
                'snippet': m['snippet']
            })
        return detailed_messages
    except Exception as e:
        return [{"error": str(e)}]

def get_gmail_message_details(message_id: str) -> Dict[str, Any]:
    """Retrieves full details of a specific email message including subject and sender.
    
    Args:
        message_id: The unique ID of the Gmail message.
    """
    try:
        service = get_gmail_service()
        message = service.users().messages().get(userId='me', id=message_id).execute()
        payload = message.get('payload', {})
        headers = payload.get('headers', [])
        
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown Date')
        
        return {
            'id': message['id'],
            'threadId': message['threadId'],
            'from': sender,
            'subject': subject,
            'date': date,
            'snippet': message['snippet'],
            'body': message['snippet'] # In a real implementation we'd parse multi-part body
        }
    except Exception as e:
        return {"error": str(e)}

def reply_to_gmail_message(message_id: str, body: str) -> str:
    """Replies to an existing email message.
    
    Args:
        message_id: The ID of the message to reply to.
        body: The content of your reply.
    """
    try:
        service = get_gmail_service()
        # Get original message for headers
        original = service.users().messages().get(userId='me', id=message_id).execute()
        headers = original['payload']['headers']
        
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
        if not subject.lower().startswith('re:'):
            subject = f"Re: {subject}"
        
        # When replying, we usually send back to the 'From' or 'Reply-To' address
        to = next((h['value'] for h in headers if h['name'].lower() == 'reply-to'), 
                  next((h['value'] for h in headers if h['name'].lower() == 'from'), ''))
        
        thread_id = original['threadId']
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        # Proper threading headers
        msg_id_header = next((h['value'] for h in headers if h['name'].lower() == 'message-id'), None)
        if msg_id_header:
            message['In-Reply-To'] = msg_id_header
            message['References'] = msg_id_header
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId='me', body={'raw': raw, 'threadId': thread_id}).execute()
        
        return f"Reply successfully sent to {to}"
    except Exception as e:
        return f"Error replying to email: {str(e)}"
