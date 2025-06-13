from typing import Any

from fastapi import status


class AppBaseError(Exception):
    """Base error for application"""
    def __init__(self, status_code: int, detail: Any) -> None:
        super().__init__(status_code, detail)
        self.status_code = status_code
        self.detail = detail


class BusinessLogicError(AppBaseError):
    """Base error for business logic to application"""


class ConflictError(AppBaseError):
    """Raised when a resource with the same unique field already exists."""


class EmailAlreadyTakenError(ConflictError):
    def __init__(self, email: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Account with this email: {email} is already taken",
        )
        self.email = email


class NotFoundError(AppBaseError):
    """Raised when a resource does not exist."""


class AuthorNotFoundError(NotFoundError):
    """Raised when the author does not exist"""
    def __init__(self, author_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no author with such ID: {author_id}"
        )
        self.author_id = author_id


class BookNotFoundError(NotFoundError):
    """Raised when the book does not exist"""
    def __init__(self, book_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no book with this ID: {book_id}"
        )
        self.book_id = book_id


class ReaderNotFoundError(NotFoundError):
    """Raised when the reader does not exist"""
    def __init__(self, reader_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no reader with such ID: {reader_id}"
        )
        self.reader_id = reader_id


class LibraryCardNotFoundError(NotFoundError):
    """Raised when the library_card does not exist"""
    def __init__(self, book_id: int, reader_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No record of book issue with such book_id: [{book_id}], reader_id: [{reader_id}]"
        )
        self.book_id = book_id
        self.reader_id = reader_id


class BookUnavailableError(BusinessLogicError):
    """Raised when there are no available instance of a book"""
    def __init__(self, book_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"There is no instance of the book available. with this ID: {book_id}"
        )
        self.book_id = book_id


class MaxBooksLimitReachedError(BusinessLogicError):
    """Raised when a reader has reached the maximum allowed number of borrowed books."""
    def __init__(self, reader_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Reader ID: {reader_id}, has reached the maximum allowed number of borrowed books"
        )
        self.reader_id = reader_id


class BookAlreadyReturnedError(BusinessLogicError):
    """Raised when a book has ben already returned to library"""
    def __init__(self, book_id: int, reader_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book with such book_id: [{book_id}], reader_id: [{reader_id}] already returned"
        )
        self.book_id = book_id
        self.reader_id = reader_id


class AuthError(AppBaseError):
    """Base class for authentication/authorization errors."""


class InvalidCredentialsError(AuthError):
    """Incorrect username or password."""
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password."
        )


class AccessTokenNotFoundError(AuthError):
    """Raised when access token not provided"""
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token not provided"
        )


class InvalidAccessTokenError(AuthError):
    """Raised when provided incorrect or expired access token"""
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access token incorrect or expired"
        )
