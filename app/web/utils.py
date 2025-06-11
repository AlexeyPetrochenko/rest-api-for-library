from typing import TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")


class ResponseScheme[T](GenericModel):
    status: str = "ok"
    data: T | list[T] | None = None
