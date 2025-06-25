import random
from collections.abc import Callable, Coroutine

from httpx import AsyncClient

from app.library.models import BookModel


async def test__get_books__returns_all_created_books_successfully(
    client: AsyncClient, make_book: Callable[[], Coroutine]
) -> None:
    await make_book()
    await make_book()

    response = await client.get("/library/books")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


async def test__get_books__empty_list_when_no_books(client: AsyncClient) -> None:
    response = await client.get("/library/books")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "data": []}


async def test__add_book__returns_401_when_token_absent(
    client: AsyncClient, make_book_scheme: Callable[[], Coroutine]
) -> None:
    book_sh = await make_book_scheme()

    response = await client.post("/library/books", json={"data_book": book_sh.dict()})

    assert response.status_code == 401
    assert response.json()["status"] == "unauthorized"
    assert response.json()["error_name"] == "AccessTokenNotFoundError"
    assert response.json()["detail"] == "Access token not provided"


async def test__add_book__creates_book_when_authorized(
    auth_client: AsyncClient, make_book_scheme: Callable[[], Coroutine]
) -> None:
    book_sh = await make_book_scheme()

    response = await auth_client.post("/library/books", json=book_sh.dict())

    assert response.status_code == 201


async def test__borrow_book__error_404_when_book_not_in_db(
    auth_client: AsyncClient, make_reader: Callable[[], Coroutine]
) -> None:
    reader = await make_reader()
    random_id = random.randint(1, 1000)

    response = await auth_client.post(f"/library/readers/{reader.reader_id}/borrow/{random_id}")

    assert response.status_code == 404
    assert response.json()["error_name"] == "BookNotFoundError"


async def test__borrow_book__error_409_when_quantity_less_than_one(  # type: ignore[no-untyped-def]
    auth_client: AsyncClient, make_reader, make_book
) -> None:
    reader = await make_reader()
    book = await make_book(amount=0)

    response = await auth_client.post(f"/library/readers/{reader.reader_id}/borrow/{book.book_id}")

    assert response.status_code == 409
    assert response.json()["error_name"] == "BookUnavailableError"


async def test__borrow_book__error_409_when_reader_reaches_max_books_limit(  # type: ignore[no-untyped-def]
    auth_client, make_reader, make_book
) -> None:
    reader = await make_reader()
    book = await make_book(amount=4)

    await auth_client.post(f"/library/readers/{reader.reader_id}/borrow/{book.book_id}")
    await auth_client.post(f"/library/readers/{reader.reader_id}/borrow/{book.book_id}")
    await auth_client.post(f"/library/readers/{reader.reader_id}/borrow/{book.book_id}")
    response = await auth_client.post(f"/library/readers/{reader.reader_id}/borrow/{book.book_id}")

    assert response.status_code == 409
    assert response.json()["error_name"] == "MaxBooksLimitReachedError"


async def test__borrow_book__error_404_when_reader_not_found(  # type: ignore[no-untyped-def]
    auth_client, make_book
) -> None:
    book = await make_book()
    random_id = random.randint(1, 1000)

    response = await auth_client.post(f"/library/readers/{random_id}/borrow/{book.book_id}")

    assert response.status_code == 404
    assert response.json()["error_name"] == "ReaderNotFoundError"


async def test__borrow_book__success(  # type: ignore[no-untyped-def]
    auth_client, make_book, make_reader
) -> None:
    reader = await make_reader()
    book = await make_book()

    response = await auth_client.post(f"/library/readers/{reader.reader_id}/borrow/{book.book_id}")

    assert response.status_code == 200


async def test__borrow_book__book_amount_decreased_by_one(  # type: ignore[no-untyped-def]
    auth_client, make_book, make_reader, session
) -> None:
    reader = await make_reader()
    book = await make_book(amount=3)
    response = await auth_client.post(f"/library/readers/{reader.reader_id}/borrow/{book.book_id}")

    book_from_db = await session.get(BookModel, book.book_id, populate_existing=True)
    assert response.status_code == 200
    assert book_from_db.amount == 2
