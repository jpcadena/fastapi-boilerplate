"""
A module for message in the app.utils package.
"""
import logging
from email.mime.text import MIMEText
from typing import Annotated, Union

import aiosmtplib
from fastapi import Depends
from pydantic import EmailStr

from app.config.config import get_settings
from app.config.settings import Settings
from app.core.decorators import benchmark, with_logging

logger: logging.Logger = logging.getLogger(__name__)


def create_message(
    email_to: EmailStr,
    subject: str,
    html: str,
    settings: Annotated[Settings, Depends(get_settings)],
) -> MIMEText:
    """
    Creates an email message with the given HTML content and subject
    :param email_to: The email address of the recipient
    :type email_to: EmailStr
    :param subject: The subject of the email
    :type subject: str
    :param html: Rendered template with environment variables
    :type html: str
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: Message with subject and rendered template
    :rtype: MIMEText
    """
    message: MIMEText = MIMEText(html, "html")
    message["Subject"] = subject
    message[
        "From"
    ] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = email_to
    logger.info("Message created from: %s", settings.EMAILS_FROM_EMAIL)
    return message


@with_logging
@benchmark
async def send_email_message(
    message: MIMEText,
    settings: Annotated[Settings, Depends(get_settings)],
) -> Union[bool, str]:
    """
    Sends the message to the given email address.
    :param message: Message with subject and rendered template
    :type message: MIMEText
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :return: True if the email was sent; otherwise an error message
    :rtype: Union[bool, str]
    """
    try:
        smtp: aiosmtplib.SMTP = aiosmtplib.SMTP(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
        )
        await smtp.connect()
        await smtp.send_message(message)
        logger.info("sent email to %s", message["To"])
        await smtp.quit()
        return True
    except Exception as exc:
        error_msg = f'error sending email to {message["To"]}.\n{exc}'
        logger.error(error_msg)
        return error_msg
