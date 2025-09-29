#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email.utils import make_msgid

from django.core.mail import get_connection, EmailMessage


def smtp_setup_connection():
    """Setup Django SMTP email backend connection."""
    # Django will handle SMTP connection using settings from settings.py
    # No explicit setup needed, connection is created per send operation
    return get_connection()


def smtp_send_email(
    connection, sender_email, to, subject, message_text, cc, reply_to, in_reply_to=None
):
    """Send an email using Django's SMTP backend.

    Args:
        connection: Django SMTP connection object (can be None, will use default)
        sender_email: Sender email address
        to: Recipient email address
        subject: Email subject
        message_text: Email body content
        cc: CC recipients
        reply_to: Reply-to address
        in_reply_to: Message ID to set in In-Reply-To header (optional)

    Returns:
        Message ID of the sent email
    """

    try:
        cc_list = []
        if cc:
            cc_list = [email.strip() for email in cc.split(",") if email.strip()]

        email = EmailMessage(
            subject=subject,
            body=message_text,
            from_email=sender_email,
            to=[to] if to else [],
            cc=cc_list,
            reply_to=[reply_to] if reply_to else None,
            connection=connection,
        )

        # Generate a unique message ID for tracking
        message_id = make_msgid()
        email.extra_headers["Message-ID"] = message_id

        if in_reply_to:
            email.extra_headers["In-Reply-To"] = in_reply_to

        # Send the email
        result = email.send()

        if result == 1:
            print(f"Message sent successfully! Message ID: {message_id}")
        else:
            print(f"Failed to send message. Result: {result}")

        return message_id

    except Exception as error:
        print(f"An error occurred: {error}")
        raise
