from typing import Optional

from pydantic import BaseSettings, Field, SecretStr


class PostgresSettings(BaseSettings):
    """Represents SQLAlchemy settings."""

    host: str = Field("postgres", env="SQLALCHEMY_HOST")
    port: Optional[int] = Field(5432, env="SQLALCHEMY_PORT")
    username: Optional[str] = Field(None, env="SQLALCHEMY_USERNAME")
    password: Optional[SecretStr] = Field(None, env="SQLALCHEMY_PASSWORD")
    dbname: Optional[str] = Field(None, env="SQLALCHEMY_DATABASE_NAME")


class RedisSettings(BaseSettings):
    """Represents Redis settings."""

    host: str = Field("redis", env="REDIS_HOST")
    port: int = Field(6379, env="REDIS_PORT")
    db: int = Field(0, env="REDIS_DB")


class PytestSettings(BaseSettings):
    """Represents Pytest settings settings."""

    test_url: str = Field("http://127.0.0.1:3000", env="TEST_URL")
    ping_backoff_timeout: int = Field(30, env="PING_BACKOFF_TIMEOUT")


class TestSettings(BaseSettings):
    """Represent all Test settings settings."""

    redis_settings: RedisSettings
    pytest_settings: PytestSettings
    postgres_settings: PostgresSettings
