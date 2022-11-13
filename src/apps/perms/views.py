#!/usr/bin/env python
# @Time    : 2022/9/28 14:13
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : views.py
# @Software: PyCharm
from typing import List, Union, Type, Optional

from apps.perms.models import ResourcesMenu, ResourcesElement, MenuElement, ResourceApi, AppInfo
from apps.perms.validates import UserMenuSerializer, UserElementSerializer, AppInfoQueryModel
from common.constants import ResCodeMsgEnum, MethodEnum
from common.exceptions import APIError
from common.public_func import get_url
from extensions.consul_help import consul_service
from utils.asyncio_help import AsyncioHelp


class ResourceService(object):
    """资源业务基础类"""

    @classmethod
    def resource_asyncio_args(cls, resource: Union[ResourcesMenu, ResourceApi, ResourcesElement]) -> tuple:
        """获取资源业务规则并发参数"""
        if not resource.is_bind_actions:
            raise APIError(ResCodeMsgEnum.INTERNAL_SERVER_ERROR)
        url = consul_service.get_service(resource.service_name) + resource.api_path
        func_args = [url, 'get']
        return get_url, func_args, {}


class MenuService(ResourceService):
    """菜单业务处理类"""

    @classmethod
    def menus_to_tree(
            cls,
            menus: List[Optional[ResourcesMenu]],
            serializor: Union[Type[UserMenuSerializer]]
    ) -> List[Union[dict]]:

        first_level_munes = [i for i in menus if not i.parent_id]
        menus_tree = [
            dict(**serializor.from_orm(menu).dict(),
                 **{"children": cls.get_menu_childrens(menus, menu.id, serializor)}) for menu in first_level_munes]
        menus_tree.sort(key=lambda x: x['sort'])
        return menus_tree

    @classmethod
    def get_menu_childrens(
            cls,
            menus: List[Optional[ResourcesMenu]],
            parent_id: str,
            serializor: Union[Type[UserMenuSerializer]]
    ) -> List[Union[dict]]:

        childrens = []
        for menu in menus:
            if menu.parent_id == parent_id:
                children = dict(**serializor.from_orm(menu).dict(),
                                **{"children": cls.get_menu_childrens(menus, menu.id, serializor)})
                childrens.append(children)
        childrens.sort(key=lambda x: x['sort'])
        return childrens


class ElementService(ResourceService):
    """页面元素业务处理"""

    @classmethod
    def get_menu_elements(cls, menu_id: str) -> List[Optional[ResourcesElement]]:
        element_ids = [i.element_id for i in MenuElement.query_all(MenuElement.menu_id == menu_id)]
        menu_elements = ResourcesElement.query_all(ResourcesElement.id.in_(element_ids))
        return menu_elements

    @classmethod
    def execute_elements_actions(cls, elements: List[Union[ResourcesElement]]) -> List[Optional[ResourcesElement]]:
        funcs, func_args, func_kwargs = [list() for _ in range(3)]
        for element in elements:
            func, func_arg, func_kwarg = cls.resource_asyncio_args(element)
            funcs.append(func)
            func_args.append(func_arg)
            func_kwargs.append(func_kwarg)

        results = AsyncioHelp().run(funcs, func_args, func_kwargs)
        filter_elements = [elements[index] for index, res in enumerate(results) if res and
                           res.get('code') == ResCodeMsgEnum.SUCCESS and res['data']['has_perm']]
        return filter_elements

    @classmethod
    def serliazer_element(
            cls,
            element: ResourcesElement,
            serializor: Union[Type[UserElementSerializer]]
    ) -> dict:
        return serializor.from_orm(element).dict()


class ApiServer(ResourceService):
    """api资源业务处理"""

    @classmethod
    def get_api(cls, api_method: MethodEnum, api_endpoint: str) -> Optional[ResourceApi]:
        api = ResourceApi.query_all(ResourceApi.method == api_method, ResourceApi.endpoint == api_endpoint,
                                    use_list=False)
        return api

    @classmethod
    def execute_api_action(cls, api: ResourceApi) -> bool:
        func, func_arg, func_kwarg = cls.resource_asyncio_args(api)
        res = AsyncioHelp().run([func], [func_arg], [func_kwarg])[0]
        res = True if res and res.get('code') == ResCodeMsgEnum.SUCCESS and res['data']['has_perm'] else False
        return res


class AppInfoServer(object):
    """app_info 业务处理"""

    @classmethod
    def get_list_options(cls, app_info_cls: Type[AppInfo], query_params: AppInfoQueryModel) -> list:
        # ToDo 封装同一的filter组件
        filter_options = []
        if query_params.app_code:
            filter_options.append(app_info_cls.app_code == query_params.app_code)
        if query_params.app_name:
            filter_options.append(app_info_cls.app_name.like(f'{query_params.app_name}%'))
        return filter_options






