#!/usr/bin/env python
# @Time    : 2022/10/8 18:46
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : __init__.py.py
# @Software: PyCharm
from flask import Blueprint


from apps.user.apis import (
    UserMenuView,
    UserElementView,
    UserApiView
)
from common.public_func import register_api


user_bp = Blueprint('user', __name__)

register_api(user_bp, UserMenuView, '/user_menus')
register_api(user_bp, UserElementView, '/user_elements')
register_api(user_bp, UserApiView, '/user_apis')
