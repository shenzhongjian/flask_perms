#!/usr/bin/env python
# @Time    : 2022/9/28 15:55
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : models.py
# @Software: PyCharm
from datetime import datetime

from src.extensions.sqlalchemy_db import db


class BaseModel(object):
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
