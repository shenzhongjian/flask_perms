#!/usr/bin/env python
# @Time    : 2022/9/9 16:07
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : constants.py
# @Software: PyCharm
from libs.enums import IntegerChoices, Choices


class ResCodeMsgEnum(IntegerChoices):
    """响应状态码"""

    SUCCESS = 0, "OK!"
    UNAUTHORIZED = 10001, "Unauthorized!"
    INTERNAL_SERVER_ERROR = 10000, "Internal Server Error!"
    CONNECTION_ERROR = 10002, "远程服务调用失败！"
    MISSING_REQUIRED_PARAM = 10003, "The required parameter is missing!"

    RE_APP_CODE = 10010, "重复的app编码!"
    RE_APP_NAME = 10011, "重复的app名称!"



class WhetherEnum(Choices):
    """是/否， 枚举类型"""

    IS = "是"
    NO = "否"


class MethodEnum(Choices):
    """请求类型枚举"""

    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    DELETE = "DELETE"


