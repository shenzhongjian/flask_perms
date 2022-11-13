#!/usr/bin/env python
# @Time    : 2022/9/28 14:13
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : models.py
# @Software: PyCharm
from apps.perms.constants import ElementTypeEnum, PermissionTypeEnum, AppInfoColumnTypeEnum
from common.constants import MethodEnum
from common.models import BaseModel
from common.public_func import gen_id
from extensions.sqlalchemy_db import db, CRUDMixin


class ResourcesMenu(db.Model, BaseModel, CRUDMixin):
    """菜单表"""
    __tablename__ = 'res_menu'
    id = db.Column(db.String(32), default=gen_id, primary_key=True)
    menu_name = db.Column(db.String(50), doc='菜单名称')
    sort = db.Column(db.Integer, doc='排序')
    path = db.Column(db.String(255), doc='菜单对应路径')
    hidden = db.Column(db.BOOLEAN, doc='是否隐藏', default=False)
    components = db.Column(db.JSON, doc='组件')
    menu_code = db.Column(db.String(50), doc='菜单编码')
    query_code = db.Column(db.String(255), doc='查询编码')
    parent_id = db.Column(db.String(32), doc='父id')
    perm_id = db.Column(db.String(32), db.ForeignKey('permission.id'))
    is_bind_actions = db.Column(db.BOOLEAN, doc='是否绑定业务规则校验', default=False)
    service_name = db.Column(db.String(50), doc='业务规则所在服务名称')
    api_path = db.Column(db.String(50), doc='api路径正则')


class ResourcesElement(db.Model, BaseModel, CRUDMixin):
    """元素资源表"""
    __tablename__ = 'res_element'
    id = db.Column(db.String(32), default=gen_id, primary_key=True)
    element_name = db.Column(db.String(50), doc='元素名称')
    element_type = db.Column(db.Enum(ElementTypeEnum), doc='元素类型')
    element_code = db.Column(db.String(50), doc='元素编码')
    is_bind_actions = db.Column(db.BOOLEAN, doc='是否绑定业务规则校验', default=False)
    service_name = db.Column(db.String(50), doc='业务规则所在服务名称')
    api_path = db.Column(db.String(255), doc='业务规则路径')
    perm_id = db.Column(db.String(32), db.ForeignKey('permission.id'))


class MenuElement(db.Model, BaseModel, CRUDMixin):
    """菜单元素表"""
    __tablename__ = 'menu_element'
    id = db.Column(db.String(32), default=gen_id, primary_key=True)
    menu_id = db.Column(db.String(32), db.ForeignKey('res_menu.id'))
    element_id = db.Column(db.String(32), db.ForeignKey('res_element.id'))


class Permission(db.Model, BaseModel, CRUDMixin):
    """权限表"""
    __tablename__ = 'permission'
    id = db.Column(db.String(32), default=gen_id, primary_key=True)
    perm_code = db.Column(db.String(50), doc='权限编码')
    perm_name = db.Column(db.String(50), doc='权限名称')
    perm_type = db.Column(db.Enum(PermissionTypeEnum), doc='权限类型')
    api = db.relationship('ResourceApi', backref="perm")
    menu = db.relationship('ResourcesMenu', uselist=False, backref="perm")
    element = db.relationship('ResourcesElement', uselist=False, backref="perm")


class ResourceApi(db.Model, BaseModel, CRUDMixin):
    """api资源表"""
    __tablename__ = 'res_api'
    id = db.Column(db.String(32), default=gen_id, primary_key=True)
    method = db.Column(db.Enum(MethodEnum), doc='请求类型')
    endpoint = db.Column(db.String(50), doc='api端点')
    api_name = db.Column(db.String(50), doc='api名称')
    is_bind_actions = db.Column(db.BOOLEAN, doc='是否绑定业务规则校验', default=False)
    service_name = db.Column(db.String(50), doc='业务规则所在服务名称')
    api_path = db.Column(db.String(50), doc='api路径正则')
    perm_id = db.Column(db.String(32), db.ForeignKey('permission.id'))


class AppInfo(db.Model, BaseModel, CRUDMixin):
    """api资源表"""
    __tablename__ = 'app_info'
    id = db.Column(db.String(32), default=gen_id, primary_key=True)
    app_code = db.Column(db.String(50), doc='应用编码')
    app_name = db.Column(db.String(50), doc='应用名称')

    @classmethod
    def is_repeat(cls, column_value: str, column_type: AppInfoColumnTypeEnum, _id: str = None) -> bool:
        filter_options = [eval(f'cls.{column_type.value}==column_value')]
        if _id:
            filter_options.append(cls.id != _id)

        return True if cls.query_all(*filter_options) else False
