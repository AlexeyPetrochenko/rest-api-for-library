from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import load_from_env
from app.store.store import Store


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    store = Store(load_from_env())
    app.state.store = store
    await store.database.connect()
    yield
    await store.database.disconnect()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    return app
