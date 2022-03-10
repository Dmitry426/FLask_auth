from typing import Optional

from pydantic import BaseSettings, Field, SecretStr


class TestSettings(BaseSettings):
    """Represents SQLAlchemy settings."""

    postgres_host: str = Field("postgres", env="SQLALCHEMY_HOST")
    postgres_port: Optional[int] = Field(5432, env="SQLALCHEMY_PORT")
    postgres_username: Optional[str] = Field(None, env="SQLALCHEMY_USERNAME")
    postgres_password: Optional[SecretStr] = Field(None, env="SQLALCHEMY_PASSWORD")
    postgres_dbname: Optional[str] = Field(None, env="SQLALCHEMY_DATABASE_NAME")

    """Represents Pytest settings settings."""

    test_url: str = Field("http://127.0.0.1:3000", env="TEST_URL")
    ping_backoff_timeout: int = Field(30, env="PING_BACKOFF_TIMEOUT")

    """Represents Redis settings."""

    redis_host: str = Field("redis", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_db: int = Field(0, env="REDIS_DB")
