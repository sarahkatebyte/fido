"""
Gmail client for FIDO

This module handles all interactions with the Gmail API.
"""
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from typing import List, Dict, Optional

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


class GmailClient:
    def __init__(self, credentials_path: str = 'secrets/credentials.json'):
        self.credentials_path = credentials_path
        self.service = None
        self.authenticate()

    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth.
        This method:
        1. Checks if we have saved credentials (token.json)
        2. If not, opens browser for user log in
        3. Saves your credentials for next time
        """
        creds = None
        token_path = 'secrets/token.json'

        # Step 1: Check if we have saved credentials from before
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # Step 2: If credentials are missing or expired, get new ones
        if not creds or not creds.valid:
            # Only enter this block if we NEED new credentials
            if creds and creds.expired and creds.refresh_token:
                # Try to refresh expired credentials
                creds.refresh(Request())
            else:
                # No credentials exist - need to log in
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=8080)

            # Save credentials for next time
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        # Step 3: Create the Gmail API service object
        self.service = build('gmail', 'v1', credentials=creds)
        print("✓ Successfully authenticated with Gmail!")

    def search_emails(self, query: str, max_results: int = 100) -> List[Dict]:
        """
        Search for emails using Gmail query syntax.

        Args:
            query: Gmail search query (e.g., "from:amazon.com is:unread")
            max_results: Maximum number of emails to return (default: 100)

        Returns:
            List of email message IDs and thread IDs

        Example queries:
            - "is:unread" - Find unread emails
            - "from:noreply@amazon.com" - Emails from Amazon
            - "subject:receipt" - Emails with "receipt" in subject
            - "older_than:30d" - Emails older than 30 days
        """
        # Try to execute the search, but handle errors gracefully
        try:
            # Call the Gmail API to search messages
            # - userId='me' means search the authenticated user's mailbox
            # - q=query is the search string (like "is:unread")
            # - maxResults limits how many emails we get back
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            # Get the list of messages from the results
            # If no messages found, use an empty list instead
            messages = results.get('messages', [])

            # Print how many emails we found
            print(f"Found {len(messages)} emails matching query: {query}")

            # Return the list of messages
            # Each message is a dict with 'id' and 'threadId'
            return messages

        except HttpError as error:
            # If something goes wrong (like network error), print it
            print(f"An error occurred during search: {error}")
            # Return an empty list so the program doesn't crash
            return []

    def get_email_details(self, message_id: str) -> Optional[Dict]:
        """
        Get full details of a specific email message.

        Args:
            message_id: The ID of the message to retrieve

        Returns:
            Dictionary containing email details (subject, sender, body, etc.)
            Returns None if there's an error

        The returned dictionary contains:
            - id: Message ID
            - threadId: Thread ID
            - subject: Email subject line
            - from: Sender email address
            - to: Recipient email address
            - date: When the email was sent
            - snippet: First ~100 characters of the email
            - body: Full email body (plain text)
        """
        try:
            # Get the message from Gmail
            # format='full' means get all details including headers and body
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract the headers (subject, from, to, date)
            # Headers are in message['payload']['headers']
            headers = message['payload']['headers']

            # Create a dictionary to store the extracted info
            email_data = {
                'id': message['id'],
                'threadId': message['threadId'],
                'snippet': message.get('snippet', ''),  # Short preview of email
                'subject': '',
                'from': '',
                'to': '',
                'date': ''
            }

            # Loop through all headers to find the ones we care about
            for header in headers:
                # Each header has a 'name' and 'value'
                name = header['name'].lower()  # Convert to lowercase for easier matching
                value = header['value']

                # Check if this header is one we want to save
                if name == 'subject':
                    email_data['subject'] = value
                elif name == 'from':
                    email_data['from'] = value
                elif name == 'to':
                    email_data['to'] = value
                elif name == 'date':
                    email_data['date'] = value

            # Get the email body
            # This is a bit complex because emails can have different structures
            email_data['body'] = self._get_email_body(message['payload'])

            return email_data

        except HttpError as error:
            print(f"An error occurred getting email details: {error}")
            return None

    def _get_email_body(self, payload: Dict) -> str:
        """
        Extract the email body from the message payload.
        This is a helper method (starts with _ to indicate it's private/internal).

        Args:
            payload: The message payload from Gmail API

        Returns:
            The email body as plain text
        """
        # Initialize empty body
        body = ""

        # Case 1: Simple email with body directly in payload
        if 'body' in payload and 'data' in payload['body']:
            # The body is base64 encoded, so we need to decode it
            import base64
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        # Case 2: Multipart email (has multiple parts like text + HTML)
        elif 'parts' in payload:
            # Loop through each part
            for part in payload['parts']:
                # We prefer plain text over HTML
                if part['mimeType'] == 'text/plain':
                    # Decode the base64 data
                    import base64
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break  # Stop looking once we find plain text

        return body

    def delete_email(self, message_id: str) -> bool:
        """
        Permanently delete an email message.
        WARNING: This is permanent! The email gets moved into the trash which is then emptied
        the trash folder gets emptied at the end of this execution
        
        args:   
            message_id: The ID of the message to be deleted
        
        Returns: 
            True if successful, False if there was an error
        """
        try:
            # Call Gmail API to delete the message 
            # This will move it to trash first, then it gets deleted
            self.service.users().messages().delete(
                userId='me',
                id=message_id
            ).execute()

            # If we get here, IT WORKED! DOPE!
            print(f"Deleted email: {message_id}:")
            return True

        except HttpError as error:
            print(f"Error in deleting email {message_id}:")
            return False

    def archive_email(self, message_id: str) -> bool:
        """
        Archive an email message (remove from inbox, but do not delete)

        Args:   
            message_id: The ID of the message to archive

        Returns: 
            True if successful, False if there was an error
        """
        try:
            # Archiving = removing the INBOX label
            # We "modify" the message by removing labels
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()

        except HttpError as error: 
            print(f"Archived email: {message_id}")
            return False

# Test code - only runs when you execute this file directly
if __name__ == '__main__':
    print("Testing Gmail Client...")
    client = GmailClient()
    print("Authentication successful!")

    # Test 1: Search for emails 
    print("\n--- Test 1: Search for unread emails ---")
    emails = client.search_emails("is:unread", max_results=5)
    print(f"Found {len(emails)} unread emails")

    # Test 2: Get details of firt email (if any exist)
    if emails:
        print("\n-- Test 2: Get email details ---")
        first_email_id = emails[0]['id']
        details = client.get_email_details(first_email_id)
        if details:
            print(f"Subject: {details['subject']}")
            print(f"From: {details['from']}")
            print(f"Date: {details['date']}")
            print(f"Body preview: {details['body'][:100]}...")  #First ten results
        else:
            print("\nNo emails found to test with!")
