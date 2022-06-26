__all__ = [
    "RedisSettings",
    "SQLAlchemySettings",
    "FlaskSettings",
    "JWTSettings",
    "RateLimitSettings",
    "TracingSettings",
    "OAuthServiceSettings",
]

from enum import Enum
from typing import List, Optional

from pydantic import BaseSettings, SecretStr


class SQLAlchemySettings(BaseSettings):
    """Represents SQLAlchemy settings."""

    class Config:
        env_prefix = "SQLALCHEMY_"

    connector: str = "postgresql"
    host: str = "postgres"
    port: int = 5432
    username: str = None
    password: SecretStr = None
    database_name: str = None
    track_modifications: bool = False


class RedisSettings(BaseSettings):
    """Represents Redis settings."""

    class Config:
        env_prefix = "REDIS_"

    host: str = "redis"
    port: int = 6379
    db: int = 0


class FlaskSettings(BaseSettings):
    """Represents Flask settings."""

    class Config:
        env_prefix = "FLASK_"

    host: str = "0.0.0.0"
    port: int = 3000
    debug: bool = True
    redirect_uri: str = "localhost"


class JWTSettings(BaseSettings):
    """Represents JWT settings."""

    class Config:
        env_prefix = "JWT_"

    secret: str = None
    access_exp: int = 60
    refresh_exp: int = 7


class OAuthServiceSettings(BaseSettings):
    client_id: str
    client_secret: SecretStr
    authorize_url: str
    access_token_url: str
    info_url: str


class OAuthSettings(BaseSettings):
    """Represents OAuth settings."""

    google: OAuthServiceSettings
    vkontakte: OAuthServiceSettings
    mail: OAuthServiceSettings
    yandex: OAuthServiceSettings

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


class TracingSettings(BaseSettings):
    """Represents tracing settings."""

    class Config:
        env_prefix = "TRACING_"

    enabled: bool = False
    service_name: str = "auth"
    environment: str = "dev"
    agent_host_name: str = "127.0.0.1"
    agent_port: int = 6831


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
