#!/usr/bin/env python
# @Time    : 2022/9/28 14:13
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : validates.py
# @Software: PyCharm
from typing import List, Union

from flask import g
from pydantic import BaseModel, validator

from apps.perms.validates import UserMenuSerializer, UserElementSerializer
from apps.perms.views import ApiServer
from common.constants import MethodEnum, ResCodeMsgEnum
from common.exceptions import APIError
from common.validates import SuccessResponseModel


class UserMenuModel(UserMenuSerializer):
    children: List[Union[dict]] = []


class UserMenuResponseModel(SuccessResponseModel):
    data: Union[UserMenuModel]


class UserElementResponseModel(SuccessResponseModel):
    data: Union[UserElementSerializer]


class UserElementQueryModel(BaseModel):
    menu_id: str


class UserApiQueryModel(BaseModel):
    method: MethodEnum
    endpoint: str

    @validator('endpoint')
    def validate_endpoint(cls, value: str, values: dict) -> str:
        api = ApiServer.get_api(values.get('method'), value)
        if not api:
            raise APIError(ResCodeMsgEnum.MISSING_REQUIRED_PARAM)
        g.api = api
        return value
