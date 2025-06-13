from pydantic import EmailStr, Field

from app.base.schemes import BaseScheme


class AdminRegisterScheme(BaseScheme):
    username: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=5)


class AdminScheme(BaseScheme):
    admin_id: int
    username: str
    email: EmailStr
