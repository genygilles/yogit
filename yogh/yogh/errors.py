"""
yogh errors
"""
from enum import Enum


class ExitCode(Enum):
    """
    Exit codes used by yogh
    """

    NO_ERROR = 0
    DEFAULT_ERROR = 1
    USAGE_ERROR = 2
