#!/usr/bin/env python
# @Time    : 2022/9/8 09:58
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : public_func.py
# @Software: PyCharm
import socket
import uuid
from typing import Type, Callable, get_type_hints, NoReturn

import aiohttp
from flask import Blueprint, Response

from common.constants import ResCodeMsgEnum
from common.exceptions import APIError
from extensions.flask_extensions import MythodView
from utils.loghelper import log_instance


def gen_id() -> str:
    """生成uuid"""
    return uuid.uuid4().hex


def register_api(
        bp: Blueprint,
        view: Type[MythodView],
        url: str,
        endpoint: str = None,
        pk: str = None,
        pk_type: str = 'int'
):
    endpoint = endpoint or view.__name__
    view_func = view.as_view(endpoint)
    methods = getattr(view, "methods", None)
    if hasattr(view, 'list'):
        bp.add_url_rule(rule=url, view_func=view_func, methods=["GET", "LIST"])

    if methods is not None:

        if 'POST' in methods:
            bp.add_url_rule(rule=url, view_func=view_func, methods=['POST'])

        if other_methods := [i for i in methods if i != "POST"]:
            if pk is not None:
                url = url if url.endswith(r'/') else url + r'/'
                url = f'{url}<{pk_type}:{pk}>'
            bp.add_url_rule(url, view_func=view_func, methods=other_methods)


def error_handler(e: Type[Exception]) -> Response:
    """
    异常处理
    :param e: 异常类
    :return:
    """
    if not isinstance(e, APIError):
        log_instance.error(e)
        e = APIError(ResCodeMsgEnum.INTERNAL_SERVER_ERROR)
    res = e.to_response()
    return res


def ver(obj: Callable, **kwargs) -> NoReturn:
    """
    根据参数注解强制校验参数类型
    :param obj: 需要校验的函数引用
    :param kwargs:
    """
    hints = get_type_hints(obj)
    for param, param_type in hints.items():

        if param != 'return' and not isinstance(kwargs[param], param_type):
            log_instance.error(f"函数: {obj.__name__}, 参数：{param} 类型错误，应该是:{param_type} 类型")
            raise APIError(ResCodeMsgEnum.INTERNAL_SERVER_ERROR)


async def get_url(
        url: str,
        method: str,
        conn_timeout: float = 3,
        content_type: str = 'application/json',
        **kwargs
) -> dict:
    if 'params' not in kwargs:
        kwargs['params'] = {}
    if 'headers' not in kwargs:
        kwargs['headers'] = {}
    user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, "
                  "like Gecko) Chrome/86.0.4240.111 Safari/537.36")
    kwargs['headers']['User-Agent'] = user_agent
    kwargs['headers']['Content-Type'] = content_type
    async with aiohttp.ClientSession(headers=kwargs['headers'], conn_timeout=conn_timeout) as session:
        async with getattr(session, method)(url=url, **kwargs) as resp:
            res = resp.json() if content_type == 'application/json' else resp.text()
            return await res


def get_host_ip() -> str:
    """
    查询本机ip地址
    :return: ip
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


if __name__ == '__main__':
    print(gen_id())
    print(get_host_ip())
