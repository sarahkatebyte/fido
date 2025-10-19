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
                creds = flow.run_local_server(port=0)

            # Save credentials for next time
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        # Step 3: Create the Gmail API service object
        self.service = build('gmail', 'v1', credentials=creds)
        print("✓ Successfully authenticated with Gmail!")


# Test code - only runs when you execute this file directly
if __name__ == '__main__':
    print("Testing Gmail Client...")
    client = GmailClient()
    print("Authentication successful!")