#!/usr/bin/env python
# @Time    : 2022/9/28 14:12
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : constants.py
# @Software: PyCharm
from libs.enums import TextChoices, Choices


class ElementTypeEnum(TextChoices):
    """元素类型"""

    BUTTON = 'BUTTON', '按钮'


class PermissionTypeEnum(TextChoices):
    """权限类型"""

    MENU = 'MENU', '菜单权限'
    ELEMENT = 'ELEMENT', '元素权限'


class AppInfoColumnTypeEnum(Choices):
    """appinfo 字段类型"""

    APP_CODE = 'app_code'
    APP_NAME = 'app_name'


if __name__ == '__main__':
    print(AppInfoColumnTypeEnum.APP_CODE.value)







