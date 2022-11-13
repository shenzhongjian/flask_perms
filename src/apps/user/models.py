#!/usr/bin/env python
# @Time    : 2022/9/28 14:13
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : models.py
# @Software: PyCharm
from common.models import BaseModel
from common.public_func import gen_id
from extensions.sqlalchemy_db import db, CRUDMixin


class Role(db.Model, BaseModel, CRUDMixin):
    """角色表"""
    __tablename__ = 'role'
    id = db.Column(db.String(32), default=gen_id, primary_key=True)
    role_code = db.Column(db.String(50), doc='角色编码')
    role_name = db.Column(db.String(50), doc='角色名称')


class UserRole(db.Model, BaseModel, CRUDMixin):
    """用户角色表"""
    __tablename__ = 'user_role'
    id = db.Column(db.String(32), default=gen_id, primary_key=True)
    user_id = db.Column(db.String(32), doc='用户id')
    role_id = db.Column(db.String(32), doc='角色id')


class UserPermission(db.Model, BaseModel, CRUDMixin):
    """用户权限表"""
    __tablename__ = 'user_perm'
    id = db.Column(db.String(32), default=gen_id, primary_key=True)
    user_id = db.Column(db.String(32), doc='用户id')
    perm_id = db.Column(db.String(32), doc='权限id')


class RolePermission(db.Model, BaseModel, CRUDMixin):
    """角色权限表"""
    __tablename__ = 'role_perm'
    id = db.Column(db.String(32), default=gen_id, primary_key=True)
    role_id = db.Column(db.String(32), doc='角色id')
    perm_id = db.Column(db.String(32), doc='权限id')






