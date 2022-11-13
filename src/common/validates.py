#!/usr/bin/env python
# @Time    : 2022/9/9 16:26
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : validates.py
# @Software: PyCharm
from typing import Union

from pydantic import BaseModel


class SuccessResponseModel(BaseModel):
    """接口成功统一返回"""

    code: int
    msg: str
    data: Union[dict, list] = {}


class AddressModel(BaseModel):
    lat: str
    lng: str
    adcode: str
    address: str
    cityName: str = None
    cityAdcode: str = None
    districtName: str = None
    provinceName: str
    districtAdcode: str = None
    provinceAdcode: str


class PictureModel(BaseModel):
    id: str = None
    remarks: str = None
    createdTime: str
    modifiedTime: str = None
    deleted: bool = False
    createdBy: str = None
    modifiedBy: str = None
    refId: str
    schemaCode: str = None
    name: str
    fileExtension: str = None
    fileSize: float
    mimeType: str


class PageModel(BaseModel):
    current_page: int
    page_size: int


if __name__ == '__main__':

    a = {'current_page': 2, "page_size": 10, 'c': 55555, 'd': 555555}
    b = PageModel(**a)
    a, b = b.dict().values()
    print(a , b)

