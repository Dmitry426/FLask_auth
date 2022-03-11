import logging
from http import HTTPStatus

import pytest

logger = logging.getLogger(__name__)

user = {"login": "Test", "password": "QWERTy90!"}

access_token = {}
refresh_token = {}

change_name = {"login": "Best", "password": "QWERTysds90!"}

pytestmark = pytest.mark.asyncio
PATH = "/auth"


async def test_create_user(make_request):
    response = await make_request(
        method="POST",
        url=f"{PATH}/registration",
        json=user,
    )
    assert response.status == HTTPStatus.CREATED
    logger.info("Response status : %s", response.status)
    assert response.body["result"] == "User successfully created"
    logger.info("Response status : %s", response.body)


async def test_login_user(make_request):
    response = await make_request(
        method="POST",
        url=f"{PATH}/login",
        json=user,
    )
    assert response.status == HTTPStatus.OK
    access_token["access_token"] = response.body["access_token"]
    refresh_token["refresh_token"] = response.body["refresh_token"]
    logger.info("Response status : %s", response.status)


async def test_refresh_token(make_request):
    response = await make_request(
        method="POST",
        url=f"{PATH}/refresh",
        json=refresh_token,
    )
    assert response.status == HTTPStatus.OK
    access_token["access_token"] = response.body["access_token"]
    refresh_token["refresh_token"] = response.body["refresh_token"]
    logger.info("Response status : %s", response.status)


async def test_change_login(make_request):
    response = await make_request(
        method="POST",
        url=f"{PATH}/change",
        json=change_name,
        jwt=access_token["access_token"],
    )
    assert response.status == HTTPStatus.ACCEPTED
    logger.info("Response status : %s", response.status)


async def test_history(make_request):
    response = await make_request(
        method="GET",
        url=f"{PATH}/history",
        jwt=access_token["access_token"],
    )

    assert response.status == HTTPStatus.OK
    logger.info("Response status : %s", response.status)


async def test_logout(make_request):
    response = await make_request(
        method="POST",
        url=f"{PATH}/logout",
        jwt=access_token["access_token"],
    )

    assert response.status == HTTPStatus.CREATED
    logger.info("Response status : %s", response.status)
