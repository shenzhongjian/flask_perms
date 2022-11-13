#!/usr/bin/env python
# @Time    : 2022/9/28 14:12
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : apis.py
# @Software: PyCharm

from flask import g
from flask.views import MethodView

from apps.perms.validates import UserMenuSerializer
from apps.perms.views import MenuService
from apps.user.validates import (
    UserMenuResponseModel,
    UserElementQueryModel, UserElementResponseModel, UserApiQueryModel
)
from apps.user.views import UserMenuServer, UserElementServer, UserApiServer
from common.decorators import login_required
from common.validates import SuccessResponseModel
from extensions.siwa import siwa


class UserMenuView(MethodView):
    decorators = [login_required]

    @siwa.doc(group='user', tags=['user_menu'], resp=UserMenuResponseModel)
    def get(self):
        """获取用户菜单权限"""
        user_munes = UserMenuServer.get_user_menus(g.user_id)
        user_munes = MenuService.menus_to_tree(user_munes, UserMenuSerializer)
        return user_munes


class UserElementView(MethodView):
    decorators = [login_required]

    @siwa.doc(group='user', tags=['user_elements'], query=UserElementQueryModel, resp=UserElementResponseModel)
    def get(self, query: UserElementQueryModel):
        """获取用户页面元素权限"""
        user_menu_elements = UserElementServer.get_user_menu_elements(g.user_id, query.menu_id)
        return user_menu_elements


class UserApiView(MethodView):
    decorators = [login_required]

    @siwa.doc(group='user', tags=['user_apis'], query=UserApiQueryModel, resp=SuccessResponseModel)
    def get(self):
        """获取用户api权限"""
        has_permission = UserApiServer.has_api_permission(g.user_id, g.api)
        return {"has_permission": has_permission}
