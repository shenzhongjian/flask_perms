#!/usr/bin/env python
# @Time    : 2022/10/8 10:33
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : __init__.py.py
# @Software: PyCharm
from flask import Blueprint


from apps.perms.apis import (
    AppInfoApi
)
from common.public_func import register_api


perm_bp = Blueprint('perm', __name__)

register_api(perm_bp, AppInfoApi, '/app_infos', pk='app_id', pk_type='string')
