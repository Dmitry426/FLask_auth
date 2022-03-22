__all__ = [
    "RedisSettings",
    "SQLAlchemySettings",
    "FlaskSettings",
    "JWTSettings",
    "RateLimitSettings",
]

from enum import Enum
from typing import List, Optional

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


class RateLimitSettings(BaseSettings):
    """Represents rate limit settings."""

    class Config:
        env_prefix = "RATELIMIT_"

    class Strategy(str, Enum):
        fixed_window = "fixed-window"
        fixed_window_elastic_expiry = "fixed-window-elastic-expiry"
        moving_window = "moving-window"

    enabled: bool = False
    storage_uri: Optional[str] = "redis://localhost:6379/0"
    strategy: Strategy = Strategy.moving_window
    default: List[str] = []
    default_limits_per_method: bool = True
    key_prefix: Optional[str]
