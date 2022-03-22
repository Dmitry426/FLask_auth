__all__ = [
    "RedisSettings",
    "SQLAlchemySettings",
    "FlaskSettings",
    "JWTSettings",
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

    class Config:
        env_prefix = "flask_"

    host: str = "0.0.0.0"
    port: int = 3000
    debug: bool = True
    redirect_uri: str = "localhost"


class JWTSettings(BaseSettings):
    """Represents JWT settings."""

    secret: Optional[str] = Field(None, env="JWT_SECRET_KEY")
    access_exp: int = Field(60, env="JWT_ACCESS_TOKEN_EXPIRES")
    refresh_exp: int = Field(7, env="JWT_REFRESH_TOKEN_EXPIRES")


class OAuthServiceSettings(BaseSettings):
    client_id: str
    client_secret: str


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
