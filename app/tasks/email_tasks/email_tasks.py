"""
A module for email utilities in the app.utils package.
"""
from pathlib import Path

from fastapi import Depends
from pydantic import EmailStr

from app.config.config import (
    auth_setting,
    get_auth_settings,
    get_init_settings,
    get_settings,
)
from app.config.db.auth_settings import AuthSettings
from app.config.init_settings import InitSettings
from app.config.settings import Settings
from app.core.decorators import with_logging
from app.tasks.email_tasks.notificaction import send_email
from app.tasks.email_tasks.template import read_template_file


async def build_email_template(
    template_file: str, init_settings: InitSettings = Depends(get_init_settings)
) -> str:
    """
    Builds the email template
    :param template_file: The template file
    :type template_file: str
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    :return: The template read as a string
    :rtype: str
    """
    template_path: Path = (
        Path(init_settings.EMAIL_TEMPLATES_DIR) / template_file
    )
    template_str: str = await read_template_file(template_path, init_settings)
    return template_str


@with_logging
async def send_reset_password_email(
    email_to: EmailStr,
    username: str,
    token: str,
    settings: Settings = Depends(get_settings),
    init_settings: InitSettings = Depends(get_init_settings),
    auth_settings: AuthSettings = Depends(get_auth_settings),
) -> bool:
    """
    Sends a password reset email to a user with the given email address
    :param email_to: The email address of the user
    :type email_to: EmailStr
    :param username: The username of the user
    :type username: str
    :param token: The reset password token generated for the user
    :type token: str
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :return: True if the email was sent successfully; False otherwise
    :rtype: bool
    """
    subject: str = (
        f"{init_settings.PROJECT_NAME} -"
        f" {init_settings.PASSWORD_RECOVERY_SUBJECT} {username}"
    )
    template_str: str = await build_email_template(
        "reset_password.html", init_settings
    )
    link: str = (
        f"{auth_settings.SERVER_URL}"
        f"{auth_settings.AUTH_URL}reset-password?token={token}"
    )
    is_sent: bool = await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": init_settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "valid_hours": auth_settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
        settings=settings,
    )
    return is_sent


@with_logging
async def send_new_account_email(
    email_to: EmailStr,
    username: str,
    settings: Settings = Depends(get_settings),
    auth_settings: AuthSettings = Depends(get_auth_settings),
    init_settings: InitSettings = get_init_settings(),
) -> None:
    """
    Send a new account email
    :param email_to: The email address of the recipient with new
     account
    :type email_to: EmailStr
    :param username: Username of the recipient
    :type username: str
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    :return: None
    :rtype: NoneType
    """
    subject: str = (
        f"{init_settings.PROJECT_NAME} - "
        f"{init_settings.NEW_ACCOUNT_SUBJECT} {username}"
    )
    template_str: str = await build_email_template(
        "new_account.html", init_settings
    )
    await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": init_settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "link": auth_settings.SERVER_URL,
        },
        settings=settings,
    )


@with_logging
async def send_welcome_email(
    email_to: EmailStr,
    username: str,
    init_settings: InitSettings = Depends(get_init_settings),
    settings: Settings = Depends(get_settings),
) -> None:
    """
    Send a welcome email
    :param email_to: The email address of the recipient to welcome
    :type email_to: EmailStr
    :param username: Username of the recipient
    :type username: str
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :return: None
    :rtype: NoneType
    """
    subject: str = (
        f"{init_settings.WELCOME_SUBJECT}{init_settings.PROJECT_NAME},"
        f" {username}"
    )
    template_str: str = await build_email_template(
        "welcome.html", init_settings
    )
    await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": init_settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "link": auth_setting.SERVER_URL,
        },
        settings=settings,
    )


@with_logging
async def send_password_changed_confirmation_email(
    email_to: EmailStr,
    username: str,
    init_settings: InitSettings = Depends(get_init_settings),
    settings: Settings = Depends(get_settings),
) -> bool:
    """
    Send a password changed confirmation email
    :param email_to: The email address of the recipient with password
     changed
    :type email_to: EmailStr
    :param username: Username of the recipient
    :type username: str
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :return: True if the email was sent; otherwise false
    :rtype: bool
    """
    subject: str = (
        f"{init_settings.PASSWORD_CHANGED_CONFIRMATION_SUBJECT}" f" {username}"
    )
    template_str: str = await build_email_template(
        "password_changed_confirmation.html", init_settings
    )
    is_sent: bool = await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": init_settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
        },
        settings=settings,
    )
    return is_sent


@with_logging
async def send_delete_account_email(
    email_to: EmailStr,
    username: str,
    init_settings: InitSettings = Depends(get_init_settings),
    settings: Settings = Depends(get_settings),
) -> bool:
    """
    Send a delete account email
    :param email_to: The email address of the recipient to delete
    :type email_to: EmailStr
    :param username: Username of the recipient
    :type username: str
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :return: True if the email was sent; otherwise false
    :rtype: bool
    """
    subject: str = f"{init_settings.DELETE_ACCOUNT_SUBJECT} {username}"
    template_str: str = await build_email_template(
        "delete_account.html", init_settings
    )
    is_sent: bool = await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": init_settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
        },
        settings=settings,
    )
    return is_sent
