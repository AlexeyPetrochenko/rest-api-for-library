from typing import Any


class AppBaseError(Exception):
    """Base error for application"""
    def __init__(self, status_code: int, detail: Any) -> None:
        super().__init__(status_code, detail)
        self.status_code = status_code
        self.detail = detail


class ConflictError(AppBaseError):
    """Raised when a resource with the same unique field already exists."""


class NotFoundError(AppBaseError):
    """Raised when a resource does not exist."""


class AuthorNotFoundError(NotFoundError):
    """Raised when the author does not exist"""


class BookNotFoundError(NotFoundError):
    """Raised when the author does not exist"""
