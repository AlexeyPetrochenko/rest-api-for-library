import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.schemes import AdminScheme
from app.auth.bearer import AccessTokenBearer
from app.library.repository import LibraryRepository
from app.library.schemes import (
        AuthorCreateScheme,
        AuthorReadScheme,
        BookCreateScheme,
        BookReadScheme,
        LibraryCardCSchemes,
        ReaderCreateScheme,
        ReaderReadScheme,
)
from app.web.config import BusinessConfig
from app.web.dependencies import (
        get_business_config,
        get_library_repo,
        get_session,
)
from app.web.exceptions import (
        AuthorNotFoundError,
        BookNotFoundError,
        BookUnavailableError,
        ConflictError,
        EmailAlreadyTakenError,
        LibraryCardNotFoundError,
        MaxBooksLimitReachedError,
        ReaderNotFoundError,
)
from app.web.utils import ResponseScheme

router = APIRouter(prefix="/library")
logger = logging.getLogger(__name__)


# TODO: CRUD операции над книгами Books
@router.post("/author", status_code=status.HTTP_201_CREATED)
async def add_author(
    data_author: AuthorCreateScheme,
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[AdminScheme, Depends(AccessTokenBearer())],
) -> ResponseScheme[AuthorReadScheme]:
        try:
            author = await repository.add_author(session, data_author)
            logger.info("Author with ID: [%s] successfully added", author.author_id)
        except SQLAlchemyError as e:
            logger.info("There is already an author with this name [%s]", data_author.name)
            raise ConflictError(
                status.HTTP_409_CONFLICT,
                detail=f"There is already an author with this name [{data_author.name}]") from e
        return ResponseScheme(data=author)


@router.post("/books", status_code=status.HTTP_201_CREATED)
async def add_book(
    data_book: BookCreateScheme,
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[AdminScheme, Depends(AccessTokenBearer())],
) -> ResponseScheme[BookReadScheme]:
    try:
        book = await repository.add_book(session, data_book)
        logger.info("Book with ID: [%s] successfully added", book.book_id)
    except IntegrityError as e:
        if e.orig.pgcode == '23505':
            logger.warning("There is already a book with this isbn: [%s].", data_book.isbn)
            raise ConflictError(
                status.HTTP_409_CONFLICT,
                detail=f"There is already a book with this isbn: [{data_book.isbn}]"
            ) from e
        if e.orig.pgcode == '23503':
            logger.warning("There is no author with such ID: [%s]", data_book.author_id)
            raise AuthorNotFoundError(data_book.author_id) from e
    return ResponseScheme(data=book)


@router.get("/books", status_code=status.HTTP_200_OK)
async def get_books(
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ResponseScheme[list[BookReadScheme]]:
    books = await repository.get_books(session)
    return ResponseScheme(data=list(books))


@router.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def get_book(
    book_id: int,
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[AdminScheme, Depends(AccessTokenBearer())],
) -> ResponseScheme[BookReadScheme]:
    book = await repository.get_book(session, book_id)
    if book is None:
        logger.warning("There is no book with this ID: [%s]", book_id)
        raise BookNotFoundError(book_id)
    return ResponseScheme(data=book)


@router.delete("/books/{book_id}", status_code=status.HTTP_200_OK)
async def del_book(
    book_id: int,
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[AdminScheme, Depends(AccessTokenBearer())],
) -> ResponseScheme[BookReadScheme]:
    book = await repository.del_book(session, book_id)
    if book is None:
        logger.warning("There is no book with this ID: [%s]", book_id)
        raise BookNotFoundError(book_id)
    logger.info("Book with this ID: [%s] has been deleted successfully", book_id)
    return ResponseScheme(book)


# TODO: Не добавлял возможность изменять количество книг намеренно
# TODO: Для этого лучше реализовать отдельные роуты
@router.put("/books/{book_id}", status_code=status.HTTP_200_OK)
async def update_book(
    book_id: Annotated[int, Path()],
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[AdminScheme, Depends(AccessTokenBearer())],
    title: Annotated[str | None, Body()] = None,
    author_id: Annotated[int | None, Body()] = None,
    year: Annotated[int | None, Body()] = None,
    isbn: Annotated[str | None, Body()] = None,
) -> ResponseScheme[BookReadScheme]:
    try:
        book = await repository.update_book(session, book_id, title, author_id, year, isbn)
    except IntegrityError as e:
        logger.warning("There is no author with such ID: [%s]", author_id)
        raise AuthorNotFoundError(author_id) from e  # type: ignore[arg-type]
    if book is None:
        logger.warning("There is no book with this ID: [%s]", book_id)
        raise BookNotFoundError(book_id)
    logger.info("Book with this ID: [%s] has been updated successfully", book_id)
    return ResponseScheme(data=book)


@router.get("/readers/{reader_id}/books", status_code=status.HTTP_200_OK)
async def get_books_for_reader(
    reader_id: int,
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[AdminScheme, Depends(AccessTokenBearer())],
) -> ResponseScheme[BookReadScheme]:
    books = await repository.get_books_for_reader(session, reader_id)
    return ResponseScheme(data=list(books))


# TODO: CRUD операции над Читателями Readers
@router.post("/readers", status_code=status.HTTP_201_CREATED)
async def add_reader(
    data_reader: ReaderCreateScheme,
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ResponseScheme[ReaderReadScheme]:
    try:
        reader = await repository.add_reader(session, data_reader)
        logger.info("Reader with ID: [%s] successfully added", reader.reader_id)
    except SQLAlchemyError as e:
        logger.info("There is already an reader with this email [%s]", data_reader.email)
        raise EmailAlreadyTakenError(data_reader.email) from e
    return ResponseScheme(data=reader)


@router.get("/readers", status_code=status.HTTP_200_OK)
async def get_readers(
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[AdminScheme, Depends(AccessTokenBearer())],
) -> ResponseScheme[list[ReaderReadScheme]]:
    readers = await repository.get_readers(session)
    return ResponseScheme(data=list(readers))


@router.get("/readers/{reader_id}", status_code=status.HTTP_200_OK)
async def get_reader(
    reader_id: int,
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[AdminScheme, Depends(AccessTokenBearer())],
) -> ResponseScheme[ReaderReadScheme]:
    reader = await repository.get_reader(session, reader_id)
    if reader is None:
        logger.warning("There is no reader with this ID: [%s]", reader_id)
        raise ReaderNotFoundError(reader_id)
    return ResponseScheme(data=reader)


@router.delete("/readers/{reader_id}", status_code=status.HTTP_200_OK)
async def del_reader(
    reader_id: int,
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[AdminScheme, Depends(AccessTokenBearer())],
) -> ResponseScheme[ReaderReadScheme]:
    reader = await repository.del_reader(session, reader_id)
    if reader is None:
        logger.warning("There is no reader with this ID: [%s]", reader_id)
        raise ReaderNotFoundError(reader_id)
    logger.info("Reader with this ID: [%s] has been deleted successfully", reader_id)
    return ResponseScheme(data=reader)


@router.put("/readers/{reader_id}", status_code=status.HTTP_200_OK)
async def update_reader(
    reader_id: Annotated[int, Path()],
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[AdminScheme, Depends(AccessTokenBearer())],
    name: Annotated[str | None, Body()] = None,
    email: Annotated[EmailStr | None, Body()] = None,
) -> ResponseScheme[ReaderReadScheme]:
    try:
        reader = await repository.update_reader(session, reader_id, name, email)
    except IntegrityError as e:
        logger.info("There is already an reader with this email [%s]", email)
        raise EmailAlreadyTakenError(email) from e  # type: ignore[arg-type]
    if reader is None:
        logger.warning("There is no reader with this ID: [%s]", reader_id)
        raise ReaderNotFoundError(reader_id)
    return ResponseScheme(data=reader)


# TODO: Бизнес логика выдачи и возврата книг читателям
@router.post("/readers/{reader_id}/borrow/{book_id}", status_code=status.HTTP_200_OK)
async def borrow_book(
    book_id: int,
    reader_id: int,
    config: Annotated[BusinessConfig, Depends(get_business_config)],
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[AdminScheme, Depends(AccessTokenBearer())],
) -> ResponseScheme[LibraryCardCSchemes]:
    book = await repository.get_book(session, book_id)

    if book is None:
        logger.warning("There is no book with this ID: [%s]", book_id)
        raise BookNotFoundError(book_id)

    if book.amount < 1:
        logger.warning("There is no instance of the book available. with this ID [%s]", book_id)
        raise BookUnavailableError(book_id)

    number_books_issued = await repository.count_reader_books(session, reader_id)
    if number_books_issued >= config.max_books_per_reader:
        logger.warning("The reader ID: [%s], has the maximum number of books", reader_id)
        raise MaxBooksLimitReachedError(reader_id)

    try:
        record = await repository.borrow_book(session, book, reader_id)
        logger.info(
            "A book issue record has been created. record ID: [%s]", record.library_card_id
        )
    except IntegrityError as e:
        logger.warning("There is no reader with such ID: [%s]", reader_id)
        raise ReaderNotFoundError(reader_id) from e
    return ResponseScheme(data=record)


@router.post("/readers/{reader_id}/returns/{book_id}", status_code=status.HTTP_200_OK)
async def return_book(
    book_id: int,
    reader_id: int,
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[AdminScheme, Depends(AccessTokenBearer())],
) -> ResponseScheme[LibraryCardCSchemes]:
    record = await repository.get_unreturned_library_record(session, book_id, reader_id)
    if record is None:
        logger.warning(
            "No unreturned record of book issue with such book_id: [%s], reader_id: [%s]",
            book_id,
            reader_id,
        )
        raise LibraryCardNotFoundError(book_id, reader_id)
    book = await repository.get_book(session, book_id)
    if book is None:
        logger.warning("There is no book with this ID: [%s]", book_id)
        raise BookNotFoundError(book_id)
    await repository.return_book(session, book, record)
    logger.info(
        "The book ID: [%s] was successfully returned by the reader: [%s]", book_id, reader_id
    )
    return ResponseScheme(body=record)
