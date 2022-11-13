#!/usr/bin/env python
# @Time    : 2022/9/28 14:13
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : validates.py
# @Software: PyCharm
from typing import Union, List

from flask import g
from pydantic import BaseModel, validator, Field

from apps.perms.constants import AppInfoColumnTypeEnum
from apps.perms.models import AppInfo
from common.constants import ResCodeMsgEnum
from common.exceptions import APIError
from common.validates import PageModel, SuccessResponseModel


class UserMenuSerializer(BaseModel):
    id: str
    menu_name: str
    sort: int
    path: str = None
    hidden: bool = False
    components: list = None
    menu_code: str

    class Config:
        orm_mode = True


class UserElementSerializer(BaseModel):
    id: str
    element_code: str
    element_name: str

    class Config:
        orm_mode = True


class AppInfoQueryModel(PageModel):
    app_code: str = None
    app_name: str = None


class AppInfoSerializer(BaseModel):
    id: str
    app_code: str
    app_name: str

    class Config:
        orm_mode = True


class AppInfoListRes(SuccessResponseModel):
    data: List[Union[AppInfoSerializer]]


class AppInfoPostRes(SuccessResponseModel):
    data: Union[AppInfoSerializer]


class AppInfoPutRes(AppInfoPostRes):
    pass


class AppInfoIdBaseModel(BaseModel):
    id: str = Field(..., alias='app_id')

    @validator('id')
    def app_info_exit(cls, value: str) -> str:
        app_info = AppInfo.get_by_id(value)
        g.app_info = app_info
        return value


class AppInfoBaseModel(BaseModel):
    app_code: str
    app_name: str

    @validator('app_code')
    def app_code_is_re(cls, value: str, values: dict) -> str:
        if AppInfo.is_repeat(value, AppInfoColumnTypeEnum.APP_CODE, _id=values.get('id')):
            raise APIError(ResCodeMsgEnum.RE_APP_CODE)
        return value

    @validator('app_name')
    def app_name_is_repeat(cls, value: str, values: dict) -> str:
        if AppInfo.is_repeat(value, AppInfoColumnTypeEnum.APP_NAME, _id=values.get('id')):
            raise APIError(ResCodeMsgEnum.RE_APP_NAME)
        return value



