import asyncio
import logging
from typing import Any, Dict, Optional

import aioredis
import asyncpg
import backoff
import pytest
from aiohttp import ClientSession
from aioredis import Redis
from pydantic import BaseModel

from .settings import TestSettings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class HTTPResponse(BaseModel):
    body: Any
    headers: Dict[str, Any]
    status: int


@pytest.fixture(name="settings", scope="session")
def settings_fixture() -> TestSettings:
    return TestSettings()


@pytest.fixture(name="event_loop", scope="session")
def event_loop_fixture() -> asyncio.AbstractEventLoop:
    """Create an instance of the default event loop."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(name="http_client", scope="session")
async def http_client_fixture(settings, postgres_client, redis_client) -> ClientSession:
    """Represents HTTP client fixture.

    Add dependency fixtures `postgres_client` and `redis_client` to
    check they are ready to work.
    """
    async with ClientSession(base_url=settings.pytest_settings.test_url) as session:
        yield session


@pytest.fixture(name="make_get_request")
def make_get_request_fixture(http_client):
    """Make HTTP-request"""

    async def inner(url: str, params: Optional[Dict[str, Any]] = None) -> HTTPResponse:
        params = params or {}
        url = f"/auth/{url}"
        logger.debug("URL: %s", url)

        async with http_client.get(url, params=params) as response:
            body = await response.json()
            logger.warning("Response: %s", body)

            return HTTPResponse(
                body=body,
                headers=dict(response.headers),
                status=response.status,
            )

    return inner


@pytest.fixture(name="redis_client", scope="session")
async def redis_client_fixture(settings: TestSettings) -> Redis:
    redis = aioredis.from_url(
        f"redis://{settings.redis_settings.host}:{settings.redis_settings.port}",
        encoding="utf8",
        decode_responses=True,
    )
    await wait_for_ping(redis, settings)
    yield redis
    await redis.flushall()
    await redis.close()


@pytest.fixture(name="postgres_client", scope="session")
async def postgres_client_fixture(settings: TestSettings):
    pg_settings = settings.postgres_settings
    conn = await asyncpg.connect(
        user=pg_settings.username,
        password=pg_settings.password,
        host=pg_settings.host,
        port=pg_settings.port,
        dbname=pg_settings.dbname,
    )
    yield conn
    await conn.execute("DROP TABLE %s", pg_settings.dbname)
    await conn.close()


async def wait_for_ping(client: Redis, settings: TestSettings):
    """Wait for service client will answer to ping."""
    client_name = type(client).__name__

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(RuntimeError, ConnectionError, TimeoutError),
        max_time=settings.pytest_settings.ping_backoff_timeout,
    )
    async def _ping(inner_client):
        result = await inner_client.ping()
        if not result:
            raise RuntimeError(f"{client_name} still not ready...")

    return await _ping(client)
