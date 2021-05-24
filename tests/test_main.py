import json
from unittest import mock

from app import main
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def token_result():
    yield {
        "taobao_user_nick": "nick",
        "taobao_user_id": "1111",
        "taobao_open_uid": "openid",
        "sub_taobao_user_nick": "nick:sub",
        "sub_taobao_user_id": "2222",
        "taobao_open_sub_uid": "subopenid",
        "access_token": "token",
        "expire_time": "1600000000",
        "refresh_token": "refresh_token",
        "refresh_token_valid_time": "1600000000",
    }


@pytest.fixture
def shop_info():
    yield {
        "pic_path": "logo.png",
        "sid": 3333,
        "title": "shop",
    }


@pytest.fixture
def user(token_result, shop_info):
    user = main.User.parse_obj(token_result)
    user.shop = main.Shop.parse_obj(shop_info)
    yield user


@pytest.fixture
def client():
    yield TestClient(main.app)


@pytest.fixture
def taobao(monkeypatch, token_result, shop_info):
    mocked = mock.AsyncMock()
    mocked.top.auth.token.create.return_value = dict(
        top_auth_token_create_response=dict(token_result=json.dumps(token_result))
    )
    mocked.shop.seller.get.return_value = dict(
        shop_seller_get_response=dict(shop=shop_info)
    )
    monkeypatch.setattr("app.main.taobao", mocked)
    yield mocked


@pytest.fixture
def get_shop(monkeypatch, shop_info):
    mocked = mock.AsyncMock()
    mocked.return_value = main.Shop.parse_obj(shop_info)
    monkeypatch.setattr("app.main.get_shop", mocked)
    yield mocked


@pytest.fixture
def get_user(monkeypatch, user):
    mocked = mock.AsyncMock()
    mocked.return_value = user
    monkeypatch.setattr("app.main.get_user", mocked)
    yield mocked


@pytest.fixture
def auth(monkeypatch, user):
    mocked = mock.AsyncMock()
    mocked.return_value = user
    monkeypatch.setattr("app.main.auth", mocked)
    yield mocked


def test_login_failed(client: TestClient, auth):
    resp = client.get(
        "/admin", params=dict(error="error", error_description="error description")
    )
    assert resp.json() == {
        "code": 1,
        "data": None,
        "msg": "error:error description",
        "success": False,
    }
    auth.assert_not_awaited()

    resp = client.get("/admin")

    assert resp.json() == {
        "code": 2,
        "data": None,
        "msg": "No Code",
        "success": False,
    }
    auth.assert_not_awaited()


def test_login(client: TestClient, auth):
    client.get("/admin", params=dict(code="code"))
    auth.assert_awaited_once_with("code")


@pytest.mark.asyncio
async def test_auth(get_user, taobao, token_result):
    await main.auth("code")
    taobao.top.auth.token.create.assert_awaited_once_with(code="code")
    get_user.assert_awaited_once_with(token_result)


@pytest.mark.asyncio
async def test_get_user(get_shop, token_result, user):
    await main.get_user(token_result)
    get_shop.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_get_shop(taobao, user):
    await main.get_shop(user)
    taobao.shop.seller.get.assert_awaited_once_with(
        session=user.access_token, fields="sid,title,pic_path"
    )
