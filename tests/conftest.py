import uuid
from collections.abc import AsyncGenerator, Callable, Coroutine
from contextlib import asynccontextmanager

import pytest
from asgi_lifespan import LifespanManager
from faker import Faker
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.library.models import AuthorModel, BookModel, ReaderModel
from app.library.schemes import BookCreateScheme
from app.store.db.sqlalchemy_db import BaseModel, Database
from app.store.store import Store
from app.web.app import create_app
from app.web.config import Config, load_from_test_env


@pytest.fixture
def config() -> Config:
    return load_from_test_env()


@pytest.fixture
def store(config: Config) -> Store:
    return Store(config)


@pytest.fixture
async def database(store: Store) -> Database:
    db = store.database
    await db.connect()
    yield db
    await db.disconnect()


@pytest.fixture
async def app(store: Store) -> AsyncGenerator[FastAPI, None]:

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> None:
        await store.database.connect()
        engine = store.database.engine
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)
        yield {"store": store}
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.drop_all)
        await store.database.disconnect()

    app = create_app(lifespan=lifespan)
    async with LifespanManager(app) as manager:
        yield manager.app


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac


@pytest.fixture
async def auth_client(
    app: FastAPI, client: AsyncClient
) -> AsyncClient:
    await client.post(
        "/auth/register",
        json={"username": "admin", "email": "admin@email.ru", "password": "password"}
    )
    response = await client.post(
        "/auth/login",
        json={"email": "admin@email.ru", "password": "password"},
    )

    tokens = response.json()["data"]
    client.cookies.set("access_token", tokens["access_token"])
    client.cookies.set("refresh_token", tokens["refresh_token"])
    return client


@pytest.fixture
async def session(database: Database) -> AsyncGenerator[AsyncSession, None]:
    async with database.session_maker() as session:
        yield session


@pytest.fixture
def make_author(
    session: AsyncSession, faker: Faker
) -> Callable[[], Coroutine]:
    async def inner(name: str | None = None) -> AuthorModel:
        author = AuthorModel(
            name=name or faker.name()
        )
        session.add(author)
        await session.commit()
        return author
    return inner


@pytest.fixture
def make_book(
    session: AsyncSession, make_author: Callable[[], Coroutine], faker: Faker
) -> Callable[[], Coroutine]:
    async def inner(
        title: str | None = None,
        author_id: int | None = None,
        year: int | None = None,
        isbn: str | None = None,
        amount: int | None = None,
    ) -> BookModel:
        if author_id is None:
            author = await make_author()
        book = BookModel(
            title=title or faker.text(max_nb_chars=10),
            author_id=author_id or author.author_id,
            year=year or faker.random_int(min=1850, max=2025),
            isbn=isbn or str(uuid.uuid4()),
            amount=1 if amount is None else amount,
        )
        session.add(book)
        await session.commit()
        return book
    return inner


@pytest.fixture
def make_book_scheme(faker: Faker, make_author: Callable[[], Coroutine]) -> Callable[[], Coroutine]:
    async def inner(
        title: str | None = None,
        author_id: int | None = None,
        year: int | None = None,
        isbn: str | None = None,
        amount: int | None = None,
    ) -> BookCreateScheme:
        if author_id is None:
            author = await make_author()
        return BookCreateScheme(
            title=title or faker.text(max_nb_chars=10),
            author_id=author_id or author.author_id,
            year=year,
            isbn=isbn,
            amount=1 if amount is None else amount,
        )
    return inner


@pytest.fixture
def make_admin_data(faker: Faker) -> Callable[[str | None], dict]:
    def inner(
        username: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> dict:
        return {
        "username": username or faker.name(),
        "email": email or faker.email(),
        "password": password or faker.text(max_nb_chars=10),
        }
    return inner


@pytest.fixture
def make_reader(
    session: AsyncSession, make_author: Callable[[], Coroutine], faker: Faker
) -> Callable[[], Coroutine]:
    async def inner(
        name: str | None = None,
        email: str | None = None,
    ) -> ReaderModel:
        reader = ReaderModel(
            name=name or faker.name(),
            email=email or faker.email(),
        )
        session.add(reader)
        await session.commit()
        return reader
    return inner
