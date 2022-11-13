#!/usr/bin/env python
# @Time    : 2022/9/9 18:09
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : flask_extensions.py
# @Software: PyCharm
import typing as t

from flask import Flask, jsonify, Response, request, current_app
from flask.typing import ResponseReturnValue
from flask.views import View, MethodViewType

from common.constants import ResCodeMsgEnum
from common.exceptions import APIError
from common.json_response import JsonResponse
from common.validates import PageModel


class JsonFlask(Flask):

    def make_response(self, rv: t.Union[list, dict, None, JsonResponse]) -> Response:
        """视图函数可以直接返回: list、dict、None"""
        if rv is None or isinstance(rv, (list, dict)):
            rv = JsonResponse.success(rv)

        if isinstance(rv, JsonResponse):
            rv = jsonify(rv.to_dict())

        return super().make_response(rv)


class MythodView(View, metaclass=MethodViewType):
    """A class-based view that dispatches request methods to the corresponding
    class methods. For example, if you implement a ``get`` method, it will be
    used to handle ``GET`` requests. ::

        class CounterAPI(MethodView):
            def get(self):
                return session.get('counter', 0)

            def post(self):
                session['counter'] = session.get('counter', 0) + 1
                return 'OK'

        app.add_url_rule('/counter', view_func=CounterAPI.as_view('counter'))
    """

    def dispatch_request(self, *args: t.Any, **kwargs: t.Any) -> ResponseReturnValue:

        if request.method.lower() == 'get' and request.args:
            meth = getattr(self, 'list', None)
        else:
            meth = getattr(self, request.method.lower(), None)
        # If the request method is HEAD and we don't have a handler for it
        # retry with GET.
        if meth is None and request.method == "HEAD":
            meth = getattr(self, "get", None)

        assert meth is not None, f"Unimplemented method {request.method!r}"
        return current_app.ensure_sync(meth)(*args, **kwargs)


# noinspection PyBroadException
class MethodViewMixin:
    model_class = None
    serializer = None
    order_by = None
    page_model = PageModel

    def get_list(self, query_options: list, paginate: t.Optional[dict]):
        if not all([self.model_class, self.serializer]):
            raise APIError(ResCodeMsgEnum.INTERNAL_SERVER_ERROR)

        execute = 'self.model_class.query.filter(*query_options)'
        if self.order_by:
            for order_by_column, order_by_type in self.order_by.items():
                execute = execute + f'.order_by(self.model_class.{order_by_type}())'

        if paginate:
            execute = execute + '.paginate(*paginate.values())'
            data = [self.serializer.from_orm(i).dict() for i in eval(execute).items]
        else:
            execute = execute + '.all()'
            data = [self.serializer.from_orm(i).dict() for i in eval(execute)]

        return data

    def get_paginate(self, query_params: dict) -> t.Optional[dict]:
        try:
            paginate = self.page_model(**query_params).dict()

        except:
            paginate = None

        return paginate

    def create(self, create_json: dict) -> dict:
        assert self.model_class, "model_class is required!"
        instance = self.model_class.create(**create_json)
        return self.serializer_data(instance)

    def serializer_data(self, instance, serializer=None) -> dict:
        assert instance, 'instance is not None!'
        serializer = serializer or self.serializer
        assert serializer, "serializer is required!"
        data = serializer.from_orm(instance).dict()
        return data

    def update(self, instance, update_json: dict) -> dict:
        assert self.model_class, "model_class is required!"
        for column, value in update_json.items():
            if column != 'id' and hasattr(instance, column):
                setattr(instance, column, value)
        self.model_class.save(instance)
        return self.serializer_data(instance)

    def destroy(self, instance):
        assert instance, 'instance is required!'
        return instance.delete()




