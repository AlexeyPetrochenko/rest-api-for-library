import logging
import typing

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.library.models import (
    AuthorModel,
    BookModel,
    LibraryCardModel,
    ReaderModel,
)
from app.library.schemes import (
    AuthorCreateScheme,
    BookCreateScheme,
    ReaderCreateScheme,
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

    async def count_reader_books(self, session: AsyncSession, reader_id: int) -> int:
        stm = select(func.count(1)).where(
            and_(
                LibraryCardModel.reader_id == reader_id,
                LibraryCardModel.return_date.is_(None)
            )
        )
        result = await session.scalar(stm)
        return typing.cast(int, result)

    async def get_unreturned_library_record(
        self, session: AsyncSession, book_id: int, reader_id: int
    ) -> LibraryCardModel | None:
        stm = select(LibraryCardModel).where(and_(
            LibraryCardModel.book_id == book_id,
            LibraryCardModel.reader_id == reader_id,
            LibraryCardModel.return_date.is_(None)
            )
        )
        return await session.scalar(stm)

    async def borrow_book(
        self, session: AsyncSession, book: BookModel, reader_id: int
    ) -> LibraryCardModel:
        issue_record = LibraryCardModel(reader_id=reader_id, book_id=book.book_id)
        book.amount -= 1
        session.add_all([issue_record, book])
        await session.commit()
        return issue_record

    async def return_book(
        self, session: AsyncSession, book: BookModel, note: LibraryCardModel
    ) -> LibraryCardModel | None:
        note.return_date = func.now()
        book.amount += 1
        await session.commit()
        return note

    async def add_reader(
        self, session: AsyncSession, data_reader: ReaderCreateScheme
    ) -> ReaderModel:
        reader = ReaderModel(**data_reader.dict())
        session.add(reader)
        await session.commit()
        return reader

    async def get_readers(self, session: AsyncSession) -> typing.Sequence[ReaderModel]:
        readers = await session.scalars(select(ReaderModel))
        return readers.all()

    async def get_reader(self, session: AsyncSession, reader_id: int) -> ReaderModel | None:
        return await session.get(ReaderModel, reader_id)

    async def del_reader(self, session: AsyncSession, reader_id: int) -> ReaderModel | None:
        reader = await session.get(ReaderModel, reader_id)
        if reader is None:
            return None
        await session.delete(reader)
        return reader

    async def update_reader(
        self,
        session: AsyncSession,
        reader_id: int,
        name: str | None = None,
        email: str | None = None,
    ) -> ReaderModel | None:
        reader = await session.get(ReaderModel, reader_id)
        if reader is None:
            return None
        reader.name = name or reader.name
        reader.email = email or reader.email
        await session.commit()
        return reader
