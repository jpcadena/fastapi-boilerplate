"""
A module for http method in the app-schemas package.
"""

from enum import Enum, UNIQUE, auto, verify


@verify(UNIQUE)
class HttpMethod(Enum):
    """
    Enum representing different HTTP methods
    """

    GET = auto()
    HEAD = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()
    CONNECT = auto()
    OPTIONS = auto()
    TRACE = auto()
    PATH = auto()
