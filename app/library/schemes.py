from datetime import datetime

from pydantic import Field

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
    email: str


class ReaderReadScheme(AuthorCreateScheme):
    reader_id: int


class LibraryCardCreateSchemes(BaseScheme):
    reader_id: int
    book_id: int
    return_data: datetime
    borrow_date: datetime | None = Field(default=None)


class LibraryCardReadSchemes(LibraryCardCreateSchemes):
    library_card_id: int
