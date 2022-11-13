#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/31 12:23 下午
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : __init__.py.py
# @Software: PyCharm
from typing import Type

from flask import Flask
from config.base_config import BaseConfig
from extensions.consul_help import consul_service
from extensions.flask_extensions import JsonFlask
from extensions.siwa import siwa
from extensions.skywalking_help import skywalking_help
from extensions.sqlalchemy_db import db


def create_app(config: Type[BaseConfig]) -> JsonFlask:
    """
    :param config: 项目配置类
    :return:
    """
    app = JsonFlask(__name__)
    app.config.from_object(config)

    configure_blueprints(app)
    configure_extensions(app)
    configure_error_handlers(app)
    return app


def configure_blueprints(app: Flask):
    """
    app注册蓝图
    :param app: flask app
    :return:
    """

    from apps.perms import perm_bp
    from apps.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/permissions')
    app.register_blueprint(perm_bp, url_prefix='/permissions')


def configure_extensions(app: Flask):
    """
    app注册组件
    :param app: flask app
    :return:
    """
    db.init_app(app)
    siwa.init_app(app)
    skywalking_help.init_app(app)
    # consul_service.init_app(app)


def configure_before_handlers(app: Flask):
    """Configures the before request handlers."""


def configure_error_handlers(app: Flask):
    """Configures the error handlers."""

    # app.register_error_handler(Exception, error_handler)
