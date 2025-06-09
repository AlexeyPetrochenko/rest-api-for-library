import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.library.schemes import (
        AuthorCreateScheme,
        AuthorReadScheme,
        BookCreateScheme,
        BookReadScheme,
)
from app.store.library.repository import LibraryRepository
from app.web.dependencies import get_library_repo, get_session
from app.web.exceptions import (
        AuthorNotFoundError,
        BookNotFoundError,
        ConflictError,
)
from app.web.utils import ResponseScheme

router = APIRouter(prefix="/library")
logger = logging.getLogger(__name__)



@router.post("/author", status_code=status.HTTP_201_CREATED)
async def add_author(
    data_author: AuthorCreateScheme,
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
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
            raise AuthorNotFoundError(
                status.HTTP_404_NOT_FOUND,
                detail=f"There is no author with such ID: [{data_book.author_id}]"
            ) from e
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
) -> ResponseScheme[BookReadScheme]:
    book = await repository.get_book(session, book_id)
    if book is None:
        logger.warning("There is no book with this ID: %s", book_id)
        raise BookNotFoundError(
            status.HTTP_404_NOT_FOUND,
            f"There is no book with this ID: {book_id}"
        )
    return ResponseScheme(data=book)


@router.delete("/books/{book_id}", status_code=status.HTTP_200_OK)
async def del_book(
    book_id: int,
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ResponseScheme[BookReadScheme]:
    book = await repository.del_book(session, book_id)
    if book is None:
        logger.warning("There is no book with this ID: %s", book_id)
        raise BookNotFoundError(
            status.HTTP_404_NOT_FOUND,
            detail=f"There is no book with this ID: {book_id}"
        )
    logger.info("Book with this ID: %s has been deleted successfully", book_id)
    return ResponseScheme(book)


@router.put("/books/{book_id}", status_code=status.HTTP_200_OK)
async def update_book(
    book_id: Annotated[int, Path()],
    repository: Annotated[LibraryRepository, Depends(get_library_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    title: Annotated[str | None, Body()] = None,
    author_id: Annotated[int | None, Body()] = None,
    year: Annotated[int | None, Body()] = None,
    isbn: Annotated[str | None, Body()] = None,
) -> ResponseScheme[BookReadScheme]:
    try:
        book = await repository.update_book(session, book_id, title, author_id, year, isbn)
    except IntegrityError as e:
        logger.warning("There is no author with such ID: %s", author_id)
        raise AuthorNotFoundError(
            status.HTTP_404_NOT_FOUND, detail=f"There is no author with such ID: [{author_id}]"
        ) from e
    if book is None:
        logger.warning("There is no book with this ID: %s", book_id)
        raise BookNotFoundError(
            status.HTTP_404_NOT_FOUND,
            detail=f"There is no book with this ID: {book_id}"
        )
    logger.info("Book with this ID: %s has been updated successfully", book_id)
    return ResponseScheme(data=book)
