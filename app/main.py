import json
import logging
from typing import Generic, Optional, TypeVar

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic.generics import GenericModel
from taobaopyx.taobao import APINode, AsyncTaobaoAPIClient

from app.config import settings

logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


DataT = TypeVar("DataT")


class BaseResponse(GenericModel, Generic[DataT]):
    success: bool = True
    code: int = 0
    msg: str = ""
    data: Optional[DataT]


class Shop(BaseModel):
    pic_path: str
    sid: int
    title: str


class UserBase(BaseModel):
    taobao_user_nick: str
    taobao_user_id: int
    taobao_open_uid: str
    sub_taobao_user_nick: Optional[str]
    sub_taobao_user_id: Optional[int]
    taobao_open_sub_uid: Optional[str]
    shop: Optional[Shop]


class User(UserBase):
    access_token: str
    expire_time: int
    refresh_token: str
    refresh_token_valid_time: int


client = AsyncTaobaoAPIClient(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET, domain=settings.API_DOMAIN)

taobao = APINode(client, "taobao")


app = FastAPI(on_shutdown=[client.aclose])


@app.get(settings.REDIRECT, response_model=BaseResponse[UserBase])
async def login(
    code: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
):
    if error_response := check(code, error, error_description):
        return error_response
    user = await auth(code)
    return BaseResponse(data=user)


def check(
    code: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
) -> Optional[BaseResponse]:
    error_response = None
    if error:
        error_response = BaseResponse(success=False, code=1, msg=f"{error}:{error_description}", data=None)
    elif not code:
        error_response = BaseResponse(success=False, code=2, msg="No Code", data=None)
    return error_response


async def auth(code: str) -> User:
    resp = await taobao.top.auth.token.create(code=code)
    token_result = json.loads(resp["top_auth_token_create_response"]["token_result"])
    user = await get_user(token_result)
    return user


async def get_user(token_result: dict[str, str]) -> User:
    user = User.parse_obj(token_result)
    user.shop = await get_shop(user)
    return user


async def get_shop(user) -> Shop:
    session = user.access_token
    resp = await taobao.shop.seller.get(session=session, fields="sid,title,pic_path")
    shop_info = resp["shop_seller_get_response"]["shop"]
    return Shop.parse_obj(shop_info)
