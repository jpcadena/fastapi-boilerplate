"""
This module handles password security functions such as hashing and
 verification.
"""

import logging

from passlib.context import CryptContext

from app.exceptions.exceptions import SecurityException

logger: logging.Logger = logging.getLogger(__name__)
crypt_context: CryptContext = CryptContext(
    schemes=["bcrypt"], deprecated="auto"
)


def _raise_custom_error(error_message: str) -> None:
    """
    Raise an exception
    :param error_message: The error message to display
    :type error_message: str
    :return: None
    :rtype: NoneType
    """
    logger.error(error_message)
    raise SecurityException(error_message)


def get_password_hash(password: str) -> str:
    """
    Hash a password using the bcrypt algorithm
    :param password: The password to hash
    :type password: str
    :return: The hashed password
    :rtype: str
    """
    if not password:
        _raise_custom_error("Password cannot be empty or None")
    return crypt_context.hash(password)


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    Verifies if a plain text password matches a hashed password
    :param plain_password: The plain text password to verify
    :type plain_password: str
    :param hashed_password: The hashed password to compare against
    :type hashed_password: str
    :return: True if the passwords match, False otherwise
    :rtype: bool
    """
    if not plain_password:
        _raise_custom_error("Plain password cannot be empty or None")
    if not hashed_password:
        _raise_custom_error("Hashed password cannot be empty or None")
    return crypt_context.verify(plain_password, hashed_password)
