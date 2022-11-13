#!/usr/bin/env python
# @Time    : 2022/9/9 17:44
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : json_response.py
# @Software: PyCharm
from typing import TypeVar

from common.constants import ResCodeMsgEnum

TypeJsonResponse = TypeVar('TypeJsonResponse', bound='JsonResponse')


class JsonResponse(object):
    """
    统一的json返回格式
    """

    def __init__(self, data, code: int, msg: str):
        self.data = data if data else []
        self.code = code
        self.msg = msg

    @classmethod
    def success(
            cls,
            data=None,
            code: int = ResCodeMsgEnum.SUCCESS,
            msg: str = ResCodeMsgEnum.SUCCESS.label
    ) -> TypeJsonResponse:
        """响应成功"""

        return cls(data, code, msg)

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }
