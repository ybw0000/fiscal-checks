from enum import Enum

from pydantic_settings import BaseSettings


class Env(str, Enum):
    LOCAL = "LOCAL"
    TESTING = "TESTING"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    PREFIX: str = "/api/v1"
    PORT: int = 8000
    DEBUG: bool = False
    ENV: Env = Env.LOCAL
    LOG_LEVEL: LogLevel = LogLevel.INFO
    DB_DRIVER: str = "postgresql+asyncpg"
    DATABASE_ADMIN_USER: str
    DATABASE_ADMIN_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    SECRET_KEY: str = "super_secret_key"

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"{self.DB_DRIVER}://"
            f"{self.DATABASE_USER}:"
            f"{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}/"
            f"{self.DATABASE_NAME}"
        )

    @property
    def sync_sqlalchemy_database_uri(self) -> str:
        return (
            f"postgresql://"
            f"{self.DATABASE_USER}:"
            f"{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}/"
            f"{self.DATABASE_NAME}"
        )


settings = Settings()  # type: ignore
