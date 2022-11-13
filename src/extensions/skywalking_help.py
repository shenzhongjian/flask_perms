# main.py
from typing import NoReturn

from flask import Flask
from skywalking import agent, config


class Skywalking(object):
    """
    接入skyWalking日志系统
    """

    @staticmethod
    def configure_config(collector_address: str, service_name: str, protocol: str) -> NoReturn:
        """
        配置skywalking相关配置
        :param collector_address:
        :param service_name:
        :param protocol:
        :return:
        """

        config.init(
            collector_address=collector_address,
            service_name=service_name,
            protocol=protocol,
            logging_level='CRITICAL',
        )

    @staticmethod
    def start() -> NoReturn:
        """启动skywalking"""
        config.flask_collect_http_params = True  # flask接收到的http参数也保存
        agent.start()

    def init_app(self, app: Flask) -> NoReturn:
        """
        :param app: flask app
        :return:
        """
        skywalking_setting = app.config.get("SKYWALKING_SETTINGS")
        if skywalking_setting:
            self.configure_config(
                skywalking_setting.get("collector_address"),
                skywalking_setting.get("service_name"),
                skywalking_setting.get("protocol")
            )
            self.start()


skywalking_help = Skywalking()
