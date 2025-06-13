import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

import bcrypt
import jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from app.web.config import Config

bcrypt.__about__ = bcrypt  # type: ignore[attr-defined]
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(password, hashed_password)
    except UnknownHashError:
        return False


def create_access_token(
    user_data: dict,
    config: Config,
    expiry: timedelta | None = None,
    refresh: bool = False,
) -> str:
    payload: dict[str, Any] = {}
    payload["current_user"] = user_data
    payload["exp"] = datetime.utcnow() + (expiry or timedelta(seconds=config.JWT_EXP))
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh
    return jwt.encode(payload=payload, key=config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def decode_token(token: str, config: Config) -> dict | None:
    try:
        return jwt.decode(jwt=token, key=config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
    except jwt.PyJWTError as e:
        logger.error("Error decoding access token: %s - %s", e.__class__.__name__, e)
        return None
