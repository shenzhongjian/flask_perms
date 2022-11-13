#!/usr/bin/env python
# @Time    : 2022/9/8 16:17
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : exceptions.py
# @Software: PyCharm
from flask import Response, make_response

from common.constants import ResCodeMsgEnum


class APIError(Exception):
    """API错误"""

    def __init__(self, code: int, msg: str = None, status_code: int = 200):
        """Initializer

        Args:
            code: 错误码
            msg: 错误描述
            status_code: HTTP状态码
        """
        super().__init__()
        self.ERRORS = dict(dict(ResCodeMsgEnum.choices))
        self.code = code
        self.msg = msg or self.ERRORS.get(code, 'Undefined')
        self.status_code = status_code

    def to_response(self) -> Response:
        """转换为flask.Response"""
        resp_data = {
            'code': self.code,
            'msg': self.msg,
            'data': {}
        }
        return make_response(resp_data, self.status_code)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.code}, {self.msg!r})'

    def __str__(self):
        return f'{self.msg!r}'
