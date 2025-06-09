import logging
import typing

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.library.models import AuthorModel, BookModel
from app.library.schemes import (
    AuthorCreateScheme,
    BookCreateScheme,
)

if typing.TYPE_CHECKING:
    from app.store.store import Store


logger = logging.getLogger(__name__)


class LibraryRepository:
    def __init__(self, store: "Store") -> None:
        self.store = store

    async def add_author(
        self, session: AsyncSession, data_author: AuthorCreateScheme
    ) -> AuthorModel:
        author = AuthorModel(name=data_author.name)
        session.add(author)
        await session.commit()
        return author

    async def add_book(
        self, session: AsyncSession, data_book: BookCreateScheme
    ) -> BookModel:
        book = BookModel(**data_book.dict())
        session.add(book)
        await session.commit()
        return book

    async def get_books(self, session: AsyncSession) -> typing.Sequence[BookModel]:
        books = await session.scalars(select(BookModel))
        return books.all()

    async def get_book(self, session: AsyncSession, book_id: int) -> BookModel | None:
        return await session.scalar(select(BookModel).where(BookModel.book_id == book_id))

    async def del_book(self, session: AsyncSession, book_id: int) -> BookModel | None:
        book = await session.get(BookModel, book_id)
        if book is None:
            return None
        await session.delete(book)
        return book

    async def update_book(
        self,
        session: AsyncSession,
        book_id: int,
        title: str | None = None,
        author_id: int | None = None,
        year: int | None = None,
        isbn: str | None = None
) -> BookModel | None:
        book = await session.get(BookModel, book_id)
        if book is None:
            return None
        book.title = title or book.title
        book.author_id = author_id or book.author_id
        book.year = year or book.year
        book.isbn = isbn or book.isbn
        await session.commit()
        return book
