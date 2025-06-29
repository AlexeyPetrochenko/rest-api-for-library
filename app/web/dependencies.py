from typing import Annotated, cast

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.repository import AdminRepository
from app.library.repository import LibraryRepository
from app.store.store import Store
from app.web.config import BusinessConfig, Config


def get_store(request: Request) -> Store:
    return cast(Store, request.state.store)


async def get_session(store: Annotated[Store, Depends(get_store)]) -> AsyncSession:
    async with store.database.session_maker() as session:
        yield session


def get_library_repo(store: Annotated[Store, Depends(get_store)]) -> LibraryRepository:
    return store.library_repo


def get_admin_repo(store: Annotated[Store, Depends(get_store)]) -> AdminRepository:
    return store.admin_repo


def get_business_config(store: Annotated[Store, Depends(get_store)]) -> BusinessConfig:
    return store.config.business_config


def get_config(store: Annotated[Store, Depends(get_store)]) -> Config:
    return store.config
