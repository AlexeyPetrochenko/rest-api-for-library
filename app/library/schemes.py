from datetime import datetime

from pydantic import EmailStr, Field

from app.base.schemes import BaseScheme


class AuthorCreateScheme(BaseScheme):
    name: str


class AuthorReadScheme(AuthorCreateScheme):
    author_id: int


class BookCreateScheme(BaseScheme):
    title: str
    author_id: int
    year: int | None
    isbn: str | None
    amount: int = Field(default=1, ge=0)


class BookReadScheme(BookCreateScheme):
    book_id: int


class ReaderCreateScheme(BaseScheme):
    name: str
    email: EmailStr


class ReaderReadScheme(AuthorCreateScheme):
    reader_id: int


class LibraryCardCSchemes(BaseScheme):
    library_card_id: int
    reader_id: int
    book_id: int
    borrow_date: datetime
    return_date: datetime | None = Field(default=None)
