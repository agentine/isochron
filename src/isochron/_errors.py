"""Exception hierarchy for isochron."""

from __future__ import annotations


class ISO8601Error(ValueError):
    """Base exception for all ISO 8601 parsing/formatting errors."""


class ParseError(ISO8601Error):
    """Raised when an input string cannot be parsed as valid ISO 8601."""

    def __init__(self, message: str, string: str = "", position: int | None = None) -> None:
        self.string: str = string
        self.position: int | None = position
        if string:
            detail = repr(string)
            if position is not None:
                detail += f" at position {position}"
            message = f"{message}: {detail}"
        super().__init__(message)


class FormatError(ISO8601Error):
    """Raised when a value cannot be formatted as ISO 8601."""
