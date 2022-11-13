#!/usr/bin/env python
# @Time       : 2022/9/2 上午9:44
# @Author     : shenzj
# @Email      : shenzj@keenon.com
# @File       : consul_help.py
# @Software: PyCharm
from random import choice
from typing import Any
from urllib.parse import urljoin

import consul
import requests
import yaml
from flask import Flask

from common.constants import ResCodeMsgEnum
from common.exceptions import APIError
from common.public_func import gen_id, get_host_ip
from utils.loghelper import log_instance


class ConsulBaseService:

    def __init__(
            self,
            consul_ip: str = None,
            consul_port: int = None,
            consul_token: str = None,
            health_check: str = None,
            timeout: str = None,
            deregister: str = None
    ):
        """
        :param consul_ip: consul服务ip
        :param consul_port: consul服务port
        :param consul_token: consul服务token密码
        :param health_check: consul健康检查频率， example: "10s"
        :param timeout: 健康检查超时时间, example: "10s"
        :param deregister: 服务不可用后自动注销时间，example: "10s"
        """
        self.host = consul_ip
        self.port = consul_port
        self.token = consul_token
        self.health_check = health_check
        self.timeout = timeout
        self.deregister = deregister
        self.service_weight = {}
        self._http = requests.session()
        self.user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, "
                           "like Gecko) Chrome/86.0.4240.111 Safari/537.36")

        self.consul = consul.Consul(host=self.host, port=self.port, token=self.token)

    def register(
            self,
            name: str,
            service_id: str,
            address: str,
            port: int,
            tags: list
    ):
        """
        Service register
        :param name: 注册到consul上的服务名称
        :param service_id: 自定义服务id
        :param address: 注册到consul的服务ip
        :param port: 注册到consul服务的port
        :param tags: 自定义服务标记
        :return:
        """
        check = consul.Check.tcp(
            host=address,
            port=port,
            interval=self.health_check,
            timeout=self.timeout,
            deregister=self.deregister
        )

        self.consul.agent.service.register(
            name=name,
            service_id=service_id,
            address=address,
            port=port,
            tags=tags,
            check=check)

    def get_service(self, name: str) -> str:
        """
        获取服务url
        :param name: 服务名称
        :return: 对应服务url
        """
        _, nodes = self.consul.health.service(service=name, passing=True)
        assert len(nodes), 'service is empty.'
        services = [f"http://{node['Service']['Address']}:{node['Service']['Port']}" for node in nodes]
        service = choice(services)
        return service

    def _request(
            self,
            service_name: str,
            method: str,
            url_or_endpoint: str,
            **kwargs
    ):
        """
        :param service_name: 调用服务名称
        :param method: 请求方法， example: 'post'
        :param url_or_endpoint: 请求路径， example: '/api/users'
        :param kwargs:
        :return: http响应
        """

        uri = self.get_service(service_name)
        url = urljoin(uri, url_or_endpoint)
        if 'params' not in kwargs:
            kwargs['params'] = {}
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['User-Agent'] = self.user_agent
        kwargs['headers']['Host'] = uri.replace("http://", "")
        if isinstance(kwargs.get('json', ''), dict):
            kwargs['headers']['Content-Type'] = 'application/json'
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        res = self._http.request(
            method=method,
            url=url,
            **kwargs
        )
        result = res.json()
        if result["errcode"] != ResCodeMsgEnum.SUCCESS:
            raise APIError(ResCodeMsgEnum.CONNECTION_ERROR)
        return result

    def set_config(self, consul_path: str, key: str, value: Any):
        """
        更改配置文件
        :param consul_path: 配置文件路径，如果有则更新， 没有则创建 example: 'config/application/sale_store'
        :param key: example: 'consul_settings'
        :param value: example: {"consul_ip": "t-consul.keenlon.cn"}
        :return:
        """
        data, _ = self.get_config(consul_path)
        if data:
            data[key] = value
        else:
            data = {key: value}
        self.consul.kv.put(consul_path, yaml.safe_dump(data, default_flow_style=False))

    def get_config(self, consul_path: str, key: str = None) -> Any:
        """
        获取配置
        :param consul_path: 配置文件路径，如果有则更新， 没有则创建 example: 'config/application/sale_store'
        :param key:example: 'consul_settings'
        :return:
        """
        _, data = self.consul.kv.get(consul_path)
        modify_index = data['ModifyIndex']
        if data is not None:
            data = data["Value"]
            data = yaml.load(data, Loader=yaml.FullLoader)
        return data.get(key) if key is not None else data, modify_index

    def delete_config(self, consul_path: str):
        """
        删除配置
        :param consul_path: 配置文件路径，如果有则更新， 没有则创建 example: 'config/application/sale_store'
        :return:
        """
        self.consul.kv.delete(consul_path)

    def ping(self) -> bool:
        try:
            leader = self.consul.status.leader()
            peers = self.consul.status.peers()
            is_ping = True if leader or peers else False
        except Exception as e:
            log_instance.error(e)
            is_ping = False
        return is_ping

    def init_app(self, app: Flask):
        consul_settings = app.config.get('CONSUL_SETTINGS')
        if consul_settings:
            self.__init__(**consul_settings)
            self.register(
                name=(name := app.config.get('SERVICE_NAME')),
                service_id=name + gen_id(),
                address=get_host_ip(),
                port=app.config.get('SERVICE_PORT'),
                tags=["v1", name]
            )


consul_service = ConsulBaseService()
