from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI

from app.store.store import Store
from app.web.config import load_from_env
from app.web.logger import setup_logging


class State(TypedDict):
    store: Store


@asynccontextmanager  # type: ignore[arg-type]
async def lifespan(app: FastAPI) -> None:
    store = Store(load_from_env())
    setup_logging()
    await store.database.connect()
    yield {"store": store}
    await store.database.disconnect()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    return app
