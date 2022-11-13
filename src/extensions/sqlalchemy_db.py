#!/usr/bin/env python
# @Time    : 2022/9/6 09:08
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : __init__.py
# @Software: PyCharm
from contextlib import contextmanager
from typing import Union
from urllib.parse import quote_plus as urlquote

from flask import Flask
from flask_sqlalchemy import (
    SQLAlchemy,
    SignallingSession,
    get_state)
from sqlalchemy import orm
from sqlalchemy.orm.session import Session as SessionBase

from common.exceptions import APIError
from utils.encryption import Encryption


class RoutingSession(SignallingSession):

    def __init__(self, *args, is_write: bool = None, **kwargs):
        self.is_write = is_write
        super(RoutingSession, self).__init__(*args, **kwargs)

    def get_bind(self, mapper=None, clause=None):
        """每次数据库操作(增删改查及事务操作)都会调用该方法, 来获取对应的数据库引擎(访问的数据库)"""
        state = get_state(self.app)
        if mapper is not None:
            try:
                # SA >= 1.3
                persist_selectable = mapper.persist_selectable
            except AttributeError:
                # SA < 1.3
                persist_selectable = mapper.mapped_table
            # 如果项目中指明了特定数据库，就获取到bind_key指明的数据库，进行数据库绑定
            info = getattr(persist_selectable, 'info', {})
            bind_key = info.get('bind_key')
            bind_key = bind_key if bind_key is not None else 'permission_service'
            from sqlalchemy.sql.dml import UpdateBase
            # 写操作 或者 更新 删除操作 - 访问主库
            if self._flushing or isinstance(clause, UpdateBase) or self.is_write:
                bind_key = bind_key + '_writer'
                # 返回主库的数据库引擎
                return state.db.get_engine(self.app, bind=bind_key)
            else:
                # 返回从库的数据库引擎
                bind_key = bind_key + '_read'
                return state.db.get_engine(self.app, bind=bind_key)
        return SessionBase.get_bind(self, mapper, clause)

    def set_to_write(self):
        """
        设置用写数据库
        """
        self.is_write = True


class BaseSQLAlchemy(SQLAlchemy):
    @contextmanager
    def auto_commit_db(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def init_app(self, app: Flask):
        sqlalchemy_binds = app.config.get('SQLALCHEMY_BINDS')
        if sqlalchemy_binds:
            for key, bind in sqlalchemy_binds.items():
                keyword = bind.split(':')[2].split('@')[0]
                dc_keyword = Encryption(app.config.get('SECRET_KEY')).decrypt(keyword)
                sqlalchemy_binds[key] = bind.replace(keyword, urlquote(dc_keyword))
            app.config.update(
                SQLALCHEMY_BINDS=sqlalchemy_binds
            )
        super().init_app(app)

    def create_session(self, options):
        return orm.sessionmaker(class_=RoutingSession, db=self, **options)


db = BaseSQLAlchemy()


# noinspection PyArgumentList
class CRUDMixin(object):
    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def save(self):
        """Saves the object to the database."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete the object from the database."""
        db.session.delete(self)
        db.session.commit()
        return self

    @classmethod
    def query_all(cls, *options, use_list=True):
        if use_list:
            query_result = cls.query.filter(*options).all()
        else:
            query_result = cls.query.filter(*options).first()
        return query_result

    @classmethod
    def get_by_id(
            cls,
            _id: Union[int, str],
            code: int = 0,
            message: str = None
    ):
        """根据主键获取

        Args:
            _id: 主键
            code: APIError错误码
            message: APIError错误描述

        Raises:
            APIError
        """
        try:
            return cls.query.get(_id)
        except cls.DoesNotExist:
            if code:
                raise APIError(code, message)
