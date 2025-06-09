import logging
import typing

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

if typing.TYPE_CHECKING:
    from app.store.store import Store

logger = logging.getLogger(__name__)


class BaseModel(DeclarativeBase):
    pass


class Database:
    def __init__(self, store: "Store") -> None:
        self.store = store
        self.engine: AsyncEngine | None = None
        self._db: type[DeclarativeBase] = BaseModel
        self.session_maker: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        self.engine = create_async_engine(url=self.store.config.ASYNC_DATABASE_URL)
        self.session_maker = async_sessionmaker(bind=self.engine, expire_on_commit=False)
        logger.info("Connected to database")

    async def disconnect(self) -> None:
        await self.engine.dispose()
        logger.info("Database connection closed")
