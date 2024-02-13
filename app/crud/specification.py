"""
This script contains abstract and concrete classes to represent
 specification objects.
These specification objects encapsulate the rules to filter or select
 specific data.
"""

from typing import Any

from pydantic import UUID4, EmailStr


class Specification:
    """
    Abstract base class to define specifications
    """

    def __init__(self, value: Any):
        self.value: Any = value


class IdSpecification(Specification):
    """
    Specification subclass that encapsulates an ID
    """

    def __init__(self, obj_id: UUID4):
        super().__init__(obj_id)


class EmailSpecification(Specification):
    """
    Specification subclass that encapsulates an email address
    """

    def __init__(self, email: EmailStr):
        super().__init__(email)


class UsernameSpecification(Specification):
    """
    Specification subclass that encapsulates a username
    """

    def __init__(self, username: str):
        super().__init__(username)
