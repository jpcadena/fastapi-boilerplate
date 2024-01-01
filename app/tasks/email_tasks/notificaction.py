"""
A module for email notifications in the app.utils package.
"""
import logging
from email.mime.text import MIMEText
from typing import Annotated, Any

from fastapi import Depends
from pydantic import EmailStr

from app.config.config import get_settings
from app.config.settings import Settings
from app.core.decorators import with_logging
from app.tasks.email_tasks.message import create_message, send_email_message
from app.tasks.email_tasks.template import render_template

logger: logging.Logger = logging.getLogger(__name__)


@with_logging
async def send_email(
    email_to: EmailStr,
    subject_template: str,
    html_template: str,
    environment: dict[str, Any],
    settings: Annotated[Settings, Depends(get_settings)],
) -> bool:
    """
    Send an e-mail to a recipient.
    :param email_to: The email address of the recipient
    :type email_to: EmailStr
    :param subject_template: The subject of the email
    :type subject_template: str
    :param html_template: The body of the email in HTML format
    :type html_template: str
    :param environment: A dictionary of variables used in the email
     templates
    :type environment: dict[str, Any]
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :return: True if the email was sent; otherwise false
    :rtype: bool
    """
    subject: str = render_template(subject_template, environment)
    html: str = render_template(html_template, environment)
    message: MIMEText = create_message(email_to, subject, html, settings)
    is_sent: bool = await send_email_message(message, settings)
    return is_sent
