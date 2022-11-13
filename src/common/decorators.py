#!/usr/bin/env python
# @Time    : 2022/9/15 10:08
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : decorators.py
# @Software: PyCharm
from functools import wraps
from inspect import getfullargspec
from typing import Callable

from flask import request, g

from common.constants import ResCodeMsgEnum
from common.exceptions import APIError
from common.public_func import ver


def type_ver(func: Callable) -> Callable:
    @wraps(func)
    def wrapp(*args, **kwargs):
        fun_arg = getfullargspec(func)
        # 参数，入参组和
        kwargs.update(dict(zip(fun_arg[0], args)))
        ver(func, **kwargs)
        return func(**kwargs)

    return wrapp


def login_required(func: Callable) -> Callable:
    """需要用户信息"""

    @wraps(func)
    def decorated(*args, **kwargs):
        if not (user_id := request.headers.get('user_id')):
            raise APIError(ResCodeMsgEnum.UNAUTHORIZED, status_code=401)
        g.user_id = user_id
        return func(*args, **kwargs)

    return decorated


if __name__ == '__main__':
    @type_ver
    def add(a: list, b: list):

        return a + b
