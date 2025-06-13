import logging

from fastapi import Request
from fastapi.security import HTTPBearer

from app.admin.schemes import AdminScheme
from app.auth.service import decode_token
from app.web.config import Config
from app.web.exceptions import AccessTokenNotFoundError, InvalidAccessTokenError

logger = logging.getLogger(__name__)


class AccessTokenBearer(HTTPBearer):
    async def __call__(self, request: Request) -> AdminScheme:  # type: ignore[override]
        config: Config = request.state.store.config
        token = request.cookies.get("access_token")
        if token is None:
            raise AccessTokenNotFoundError
        token_data = decode_token(token, config)
        if token_data is None:
            raise InvalidAccessTokenError
        return AdminScheme(**token_data["current_user"])


class RefreshTokenBearer(HTTPBearer):
    async def __call__(self, request: Request) -> AdminScheme:  # type: ignore[override]
        config: Config = request.state.store.config
        token = request.cookies.get("refresh_token")
        if token is None:
            raise AccessTokenNotFoundError

        token_data = decode_token(token, config)
        if token_data is None:
            raise InvalidAccessTokenError
        return AdminScheme(**token_data["current_user"])
