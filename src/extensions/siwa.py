from collections import defaultdict
from functools import wraps
from typing import Dict, List, Any, Optional, Type

import pydantic
from flask import Flask, request
from flask_siwadoc import SiwaDoc, ValidationError
from flask_siwadoc import utils
from pydantic import BaseModel


def generate_openapi(title: str,
                     version: str,
                     openapi_version: str,
                     app: Flask,
                     models: Dict[str, Dict],
                     description: str = None) -> Dict[str, Any]:
    """
    :param title:
    :param version:
    :param openapi_version:
    :param app:
    :param models:
    :param description:
    """

    routes: Dict[str:Dict] = dict()
    tags: Dict[str:Dict] = dict()
    groups: Dict[str:List] = defaultdict(list)
    for rule in app.url_map.iter_rules():
        # 视图函数
        func = old_func = app.view_functions[rule.endpoint]
        path, parameters = utils.parse_path_params(str(rule))
        methods = rule.methods
        print(methods)
        for method in methods:
            if method in ['HEAD', 'OPTIONS', "LIST"]:
                continue
            if getattr(old_func, "view_class", None):
                cls = getattr(old_func, "view_class")
                func = getattr(cls, method.lower(), None)
                if method.lower() == 'get' and 'LIST' in methods:
                    func = getattr(cls, 'list', None)
            # 只有被siwadoc装饰了函数才加入openapi
            if not getattr(func, '_decorated', None):
                continue
            if not hasattr(func, 'tags'):
                func.tags = ['default']
            if not hasattr(func, 'group'):
                func.group = ''

            func_group = getattr(func, 'group', "")
            func_tags = [tag if tag != 'default' else func_group + "/" + tag for tag in
                         getattr(func, 'tags', ['default'])]

            groups[func_group].extend(func_tags)
            tags.update({tag: {"name": tag} for tag in func_tags})
            operation = {
                'summary': utils.get_operation_summary(func),
                'description': utils.get_operation_description(func),
                'operationID': func.__name__ + '__' + method.lower(),
                'tags': func_tags,
            }

            if hasattr(func, 'body'):
                operation['requestBody'] = {
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': f'#/components/schemas/{func.body}'
                            }
                        }
                    }
                }
            if hasattr(func, 'query'):
                parameters.extend(utils.parse_other_params('query', models[func.query]))
            if hasattr(func, 'header'):
                parameters.extend(utils.parse_other_params('header', models[func.header]))
            if hasattr(func, 'cookie'):
                parameters.extend(utils.parse_other_params('cookie', models[func.cookie]))
            operation['parameters'] = parameters

            operation['responses'] = {}
            has_2xx = False
            if hasattr(func, 'x'):
                for code, msg in func.x.items():
                    if code.startswith('2'):
                        has_2xx = True
                    operation['responses'][code] = {
                        'description': msg,
                    }

            if hasattr(func, 'resp'):
                operation['responses']['200'] = {
                    'description': 'Successful Response',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': f'#/components/schemas/{func.resp}'
                            }
                        }
                    },
                }
            elif not has_2xx:
                operation['responses']['200'] = {'description': 'Successful Response'}

            if any([hasattr(func, schema) for schema in ('query', 'body')]):
                operation['responses']['400'] = {
                    'description': 'Validation Error',
                    'content': {
                        'application/json': {
                            'schema': {
                                "code": 200,
                            }
                        }
                    },
                }
            routes.setdefault(path, {})[method.lower()] = operation

    definitions = {}
    for _, schema in models.items():
        if 'definitions' in schema:
            for key, value in schema['definitions'].items():
                definitions[key] = value
            del schema['definitions']
    info = {
        'title': title,
        'version': version,
    }
    if description:
        info["description"] = description
    data = {
        'openapi': openapi_version,
        'info': info,
        'tags': list(tags.values()),
        'x-tagGroups': [{"name": k, "tags": list(set(v))} for k, v in groups.items()],
        'paths': {
            **routes
        },
        'components': {
            'schemas': {
                name: schema for name, schema in models.items()
            },
        },
        'definitions': definitions
    }
    print(data)
    return data


class NewSiwadoc(SiwaDoc):
    @property
    def openapi(self):
        if not self._openapi:
            self._openapi = generate_openapi(openapi_version=self.openapi_version,
                                             title=self.title,
                                             version=self.version,
                                             description=self.description,
                                             app=self.app,
                                             models=self.models)
        return self._openapi

    def doc(self,
            query: Optional[Type[BaseModel]] = None,
            header: Optional[Type[BaseModel]] = None,
            cookie: Optional[Type[BaseModel]] = None,
            body: Optional[Type[BaseModel]] = None,
            path: Optional[Type[BaseModel]] = None,
            resp=None,
            x=[],
            tags=[],
            group=None,
            summary=None,
            description=None,
            ):
        """
        装饰器同时兼具文档生成和请求数据校验功能
        """

        def decorate_validate(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                query_data, body_data, path_data = None, None, None
                # 注解参数
                query_in_kwargs = func.__annotations__.get("query")
                body_in_kwargs = func.__annotations__.get("body")
                path_in_kwargs = func.__annotations__.get("path")
                query_model = query_in_kwargs or query
                body_model = body_in_kwargs or body
                path_model = path_in_kwargs or path
                if query_model:
                    query_params = utils.convert_query_params(request.args, query_model)
                    query_data = query_model(**query_params)

                if path_model is not None and body_model is not None:
                    new_model = self.merge_path_body_model(body_model, path_model)
                    body_data = new_model(**(dict(**request.get_json(silent=True), **kwargs) or {}))
                    body_data = body_model(**body_data.dict())

                elif path_model is None and body_model is not None:
                    body_data = body_model(**(request.get_json(silent=True) or {}))

                elif path_model is not None and body_model is None:
                    path_model(**kwargs)

                if query_in_kwargs:
                    kwargs["query"] = query_data
                if body_in_kwargs:
                    kwargs["body"] = body_data

                return func(*args, **kwargs)

            for model, name in zip(
                    (query, header, cookie, body, resp), ('query', 'header', 'cookie', 'body', 'resp')
            ):
                if model:
                    assert issubclass(model, BaseModel)
                    self.models[model.__name__] = model.schema()
                    setattr(wrapper, name, model.__name__)

            code_msg = {}
            if code_msg:
                wrapper.x = code_msg

            if tags:
                wrapper.tags = tags
            if group:
                wrapper.group = group
            wrapper.summary = summary
            wrapper.description = description
            wrapper._decorated = True  # 标记判断改函数是否加入openapi
            return wrapper

        return decorate_validate

    @staticmethod
    def merge_path_body_model(body_model: Type[BaseModel], path_model: Type[BaseModel]) -> Type[BaseModel]:
        class NewModel(body_model, path_model):
            pass
        return NewModel


siwa = NewSiwadoc()
