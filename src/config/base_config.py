#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/31 12:23 下午
# @Author  : 沈中建
# @Email   : shenzj@keenon.com
# @File    : __init__.py.py
# @Software: PyCharm

from os import getenv
from pathlib import Path
from typing import Any, Dict, Union

from extensions.consul_help import ConsulBaseService
from utils.yaml_help import SiteYaml

CONSUL_IP = getenv('CONSUL_IP', "t-consul.keenlon.cn")
# CONSUL_IP = getenv('CONSUL_IP', "d-consul.keenlon.cn")
CONSUL_PORT = getenv('CONSUL_PORT', 80)
CONSUL_TOKEN = getenv('CONSUL_TOKEN', "80ddf50e-7a9f-be5c-a2e2-11f1813d810b")
# CONSUL_TOKEN = getenv('CONSUL_TOKEN', "41287968-07de-f17f-8676-5efbd8c028d6")
CONSUL_HEALTH_CHECK = getenv('CONSUL_HEALTH_CHECK', "10s")
CONSUL_TIMEOUT = getenv('CONSUL_TIMEOUT', "10s")
CONSUL_DEREGISTER = getenv('CONSUL_DEREGISTER', "10s")
CONSUL_PATH = getenv('CONSUL_PATH', 'config/application/user-perms-service')
# collector_address: 172.16.13.132:12800


class BaseConfig(object):

    CONSUL_SETTINGS = {
        "consul_ip": CONSUL_IP,
        "consul_port": CONSUL_PORT,
        "consul_token": CONSUL_TOKEN,
        "health_check": CONSUL_HEALTH_CHECK,
        "timeout": CONSUL_TIMEOUT,
        "deregister": CONSUL_DEREGISTER
    }

    def __init__(self):

        self.consul_service = self._get_consul_service()
        self.config_path = str(Path.cwd() / 'config/config_yaml.yml')
        self.yaml = SiteYaml(config_path=self.config_path)
        self.set_config(self.get_config())

    def _get_consul_service(self) -> Union[ConsulBaseService]:
        consul_service = ConsulBaseService(**self.CONSUL_SETTINGS)
        if not consul_service.ping():
            consul_service = None
        return consul_service

    def get_config(self, key: str = None) -> Any:
        """
        获取配置
        :param key: 配置项
        :return: 配置值
        """

        if self.consul_service:
            settings, modify_index = self.consul_service.get_config(CONSUL_PATH, key)
            current_modify_index = self.yaml.get_config('modify_index')
            if modify_index != current_modify_index:
                settings['modify_index'] = modify_index
                self.yaml.update_config(settings)
        else:
            settings = self.yaml.get_config()

        return settings

    @classmethod
    def set_config(cls, settings: Dict):
        """
        初始化配置类
        :param settings:
        :return:
        """
        for key, value in settings.items():
            setattr(BaseConfig, key.upper(), value)


config_help = BaseConfig()
