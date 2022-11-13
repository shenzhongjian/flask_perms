#!/usr/bin/env python
# @Time    : 2022/9/28 14:12
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : apis.py
# @Software: PyCharm
from flask import g

from apps.perms import validates as vl
from apps.perms.models import AppInfo
from apps.perms.views import AppInfoServer
from common.validates import SuccessResponseModel
from extensions.flask_extensions import MythodView, MethodViewMixin
from extensions.siwa import siwa


class AppInfoApi(MethodViewMixin, MythodView):
    """应用管理"""
    model_class = AppInfo
    serializer = vl.AppInfoSerializer

    @siwa.doc(group='app_info', tags=['app_info_list'], query=vl.AppInfoQueryModel, resp=vl.AppInfoListRes)
    def list(self, query: vl.AppInfoQueryModel):
        """获取应用管理列表"""
        app_infos = self.get_list(AppInfoServer.get_list_options(AppInfo, query), self.get_paginate(query.dict()))
        return app_infos

    @siwa.doc(group='app_info', tags=['app_info_create'], body=vl.AppInfoBaseModel, resp=vl.AppInfoPostRes)
    def post(self, body: vl.AppInfoBaseModel):
        """新增应用"""
        app_info = self.create(body.dict())
        return app_info

    @siwa.doc(group='app_info', tags=['app_info_update'], body=vl.AppInfoBaseModel, path=vl.AppInfoIdBaseModel,
              resp=vl.AppInfoPutRes)
    def put(self, app_id: str, body: vl.AppInfoBaseModel):
        """修改应用"""
        app_info = self.update(g.app_info, body.dict())
        return app_info

    @siwa.doc(group='app_info', tags=['app_info_delete'], path=vl.AppInfoIdBaseModel, resp=SuccessResponseModel)
    def delete(self, app_id: str):
        """删除应用"""
        self.destroy(g.app_info)
