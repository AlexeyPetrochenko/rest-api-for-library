from typing import TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class ResponseScheme[T](GenericModel):
    status: str = "ok"
    data: T | list[T] | None = None


class ErrorResponseScheme(BaseModel):
    http_status: int
    status: str = "error"
    message: str | None = None
    data: dict | list | None = None
