from typing import Annotated, cast

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.store.library.repository import LibraryRepository
from app.store.store import Store


def get_store(request: Request) -> Store:
    return cast(Store, request.state.store)


async def get_session(store: Annotated[Store, Depends(get_store)]) -> AsyncSession:
    async with store.database.session_maker() as session:
        yield session


def get_library_repo(store: Annotated[Store, Depends(get_store)]) -> LibraryRepository:
    return store.library_repo
