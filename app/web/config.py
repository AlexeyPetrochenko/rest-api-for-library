from dotenv import dotenv_values
from pydantic_settings import BaseSettings


class BusinessConfig(BaseSettings):
    max_books_per_reader: int = 3


class Config(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    JWT_SECRET: str
    JWT_ALGORITHM: str

    JWT_EXP: int = 900  # seconds
    REFRESH_JWT_EXP: int = 2  # days

    business_config: BusinessConfig = BusinessConfig()

    @property
    def ASYNC_DATABASE_URL(self) -> str:  # noqa: N802
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


# TODO: Явно через dotenv_values указываем откуда загружать переменные окружения
def load_from_env() -> Config:
    data = dotenv_values(".env")
    return Config(**data)  # type: ignore[arg-type]


def load_from_test_env() -> Config:
    data = dotenv_values(".test_env")
    return Config(**data)  # type: ignore[arg-type]

