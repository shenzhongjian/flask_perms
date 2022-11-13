#!/usr/bin/env python
# @Time    : 2022/9/28 14:13
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : views.py
# @Software: PyCharm
from typing import Union, List, Optional

from apps.perms.models import ResourcesMenu, ResourceApi, ResourcesElement
from apps.perms.validates import UserElementSerializer
from apps.perms.views import ElementService, ApiServer
from apps.user.models import UserPermission, UserRole, RolePermission


class UserServer(object):
    """用户业务规则处理"""

    @classmethod
    def get_user_perm_ids(cls, user_id: str) -> List[Optional[str]]:
        user_perms = UserPermission.query_all(UserPermission.user_id == user_id)
        user_perm_ids = [i.perm_id for i in user_perms]
        return user_perm_ids

    @classmethod
    def get_user_role_ids(cls, user_id: str) -> List[Optional[str]]:
        user_roles = UserRole.query_all(UserRole.user_id == user_id)
        user_role_ids = [i.role_id for i in user_roles]
        return user_role_ids

    @classmethod
    def get_roles_perm_ids(cls, user_id: str) -> List[Optional[str]]:
        user_role_ids = cls.get_user_role_ids(user_id)
        roles_perms = RolePermission.query_all(RolePermission.role_id.in_(user_role_ids))
        roles_perm_ids = [i.perm_id for i in roles_perms]
        return roles_perm_ids

    @classmethod
    def get_user_all_perms(cls, user_id: str) -> List[Optional[str]]:
        user_all_perm_ids = cls.get_user_perm_ids(user_id) + cls.get_roles_perm_ids(user_id)
        return user_all_perm_ids

    @classmethod
    def resource_has_permissions(
            cls,
            user_id: str,
            resources: List[Union[ResourcesMenu, ResourceApi, ResourcesElement]]
    ) -> List[Union[ResourcesMenu, ResourceApi, ResourcesElement]]:
        user_all_perm_ids = cls.get_user_all_perms(user_id)
        has_permission_resource = [resource for resource in resources if resource.perm_id in user_all_perm_ids]
        return has_permission_resource


class UserMenuServer(UserServer):
    """用户菜单资源业务处理类"""

    @classmethod
    def get_user_menus(cls, user_id: str) -> List[Optional[ResourcesMenu]]:
        # Todo 添加缓存信息
        user_all_perm_ids = cls.get_user_all_perms(user_id)
        user_menus = ResourcesMenu.query_all(ResourcesMenu.perm_id.in_(list(set(user_all_perm_ids))))
        return user_menus


class UserElementServer(UserServer):
    """用户菜单元素资源业务处理"""

    @classmethod
    def get_user_menu_elements(cls, user_id: str, menu_id: str) -> List[Optional[dict]]:
        menu_elements = ElementService.get_menu_elements(menu_id)
        user_menu_elements = cls.resource_has_permissions(user_id, menu_elements)
        need_exe_actions = [i for i in user_menu_elements if i.is_bind_actions]
        filter_exe_actions = ElementService.execute_elements_actions(need_exe_actions)
        user_menu_elements = [ElementService.serliazer_element(element, UserElementSerializer) for element in
                              [i for i in user_menu_elements if not i.is_bind_actions] + filter_exe_actions]

        return user_menu_elements


class UserApiServer(UserServer):
    """用户api资源业务处理"""

    @classmethod
    def has_api_permission(cls, user_id: str, api: ResourceApi) -> bool:
        apis = cls.resource_has_permissions(user_id, [api])
        has_permission = True if apis and ApiServer.execute_api_action(apis[0]) else False
        return has_permission
