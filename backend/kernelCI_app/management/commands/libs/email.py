#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import os
import sys

from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


TOKEN_FILE = "gmail_api_token.json"


def gmail_setup_service(credentials_file):
    """Authenticate with Gmail using OAuth2 and get credentials."""
    creds = None
    # Define the required Gmail API scope
    scopes = ["https://mail.google.com/"]

    # Load tokens if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, scopes)

    # If there are no valid credentials, initiate a new OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print(credentials_file)
            if not credentials_file or not os.path.exists(credentials_file):
                print(
                    "Missing Gmail API credentials file for the token generation. (use --credentials-file)"
                )
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service


def gmail_send_email(service, sender_email, to, subject, message_text, cc, reply_to):
    """Send an email using the Gmail API."""

    user_id = "me"
    email = create_email(sender_email, to, subject, message_text, cc, reply_to)

    try:
        sent_message = (
            service.users().messages().send(userId=user_id, body=email).execute()
        )

        full_message = (
            service.users()
            .messages()
            .get(userId=user_id, id=sent_message["id"], format="full")
            .execute()
        )

        headers = full_message["payload"]["headers"]
        message_id = next(
            (
                header["value"]
                for header in headers
                if header["name"].lower() == "message-id"
            ),
            None,
        )
        print(f"Message sent successfully! Message ID: {message_id}")

        return message_id

    except Exception as error:
        print(f"An error occurred: {error}")


def create_email(sender, to, subject, message_text, cc, reply_to):
    message = EmailMessage()
    message.set_content(message_text)
    # Set email headers
    if to:
        message["to"] = to
    if cc:
        message["cc"] = cc
    message["from"] = sender
    message["subject"] = subject
    if reply_to:
        message["Reply-To"] = reply_to

    # Encode the message as base64
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw}
