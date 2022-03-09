import logging
from http import HTTPStatus

import pytest

logger = logging.getLogger(__name__)

user = {"login": "Test", "password": "QWERTy90!"}
pytestmark = pytest.mark.asyncio


async def test_create_user(make_request):
    response = await make_request(method="POST", url="registration", json=user)
    assert response.status == HTTPStatus.CREATED
    logger.debug("Response status : %s", response.status)
    assert response.body
    logger.info("Response status : %s", response.body)
