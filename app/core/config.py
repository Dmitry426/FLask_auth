__all__ = [
    "RedisSettings",
    "SQLAlchemySettings",
    "FlaskSettings",
    "JWTSettings",
    "TracingSettings",
]

from typing import Optional

from pydantic import BaseSettings, Field, SecretStr


class SQLAlchemySettings(BaseSettings):
    """Represents SQLAlchemy settings."""

    connector: str = Field("postgresql", env="SQLALCHEMY_SCHEMA")
    host: str = Field("postgres", env="SQLALCHEMY_HOST")
    port: Optional[int] = Field(5432, env="SQLALCHEMY_PORT")
    username: Optional[str] = Field(None, env="SQLALCHEMY_USERNAME")
    password: Optional[SecretStr] = Field(None, env="SQLALCHEMY_PASSWORD")
    database_name: Optional[str] = Field(None, env="SQLALCHEMY_DATABASE_NAME")


class RedisSettings(BaseSettings):
    """Represents Redis settings."""

    host: str = Field("redis", env="REDIS_HOST")
    port: int = Field(6379, env="REDIS_PORT")
    db: int = Field(0, env="REDIS_DB")


class FlaskSettings(BaseSettings):
    """Represents Flask settings."""

    host: str = Field("0.0.0.0", env="FLASK_HOST")
    port: int = Field(3000, env="PORT_APP")
    debug: bool = Field(True, env="FLASK_DEBUG")


class JWTSettings(BaseSettings):
    """Represents JWT settings."""

    secret: Optional[str] = Field(None, env="JWT_SECRET_KEY")
    access_exp: int = Field(60, env="JWT_ACCESS_TOKEN_EXPIRES")
    refresh_exp: int = Field(7, env="JWT_REFRESH_TOKEN_EXPIRES")


class TracingSettings(BaseSettings):
    """Represents tracing settings."""

    class Config:
        env_prefix = "TRACING_"

    enabled: bool = False
    service_name: str = "auth"
    environment: str = "dev"
    agent_host_name: str = "127.0.0.1"
    agent_port: int = 6831
