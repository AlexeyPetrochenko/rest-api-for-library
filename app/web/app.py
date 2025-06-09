from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI

from app.library.routers import router as library_router
from app.store.store import Store
from app.web.config import load_from_env
from app.web.exceptions import AppBaseError
from app.web.handlers import handler_base_app_exc
from app.web.logger import setup_logging
from app.web.middlewares import ErrorHandlingMiddleware


class State(TypedDict):
    store: Store


# сделать API методы для library
# Подумать над error_response()
# Проверить разницу между default и server_default при добавлении поля
#

@asynccontextmanager  # type: ignore[arg-type]
async def lifespan(app: FastAPI) -> None:
    store = Store(load_from_env())
    setup_logging()
    await store.database.connect()
    yield {"store": store}
    await store.database.disconnect()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(ErrorHandlingMiddleware)
    app.add_exception_handler(AppBaseError, handler_base_app_exc)

    app.include_router(library_router, tags=["library"])
    return app
