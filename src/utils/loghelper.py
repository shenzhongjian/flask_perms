# -*- coding: utf-8 -*-
# @Time    : 2018-12-14 11:59
# @Author  : Will
# @Email   : 864311352@qq.com
# @File    : loghelper.py
# @Software: PyCharm

import sys
from pathlib import Path

import logbook
from logbook import Logger, TimedRotatingFileHandler, StreamHandler


class LogHelper(object):

    def __init__(self, name: str = "logging", file_path: Path = Path(__file__)):

        self.name = name
        self._file_path = file_path
        self.logger = None

        logbook.set_datetime_format("local")
        self.logger = Logger(self.name)
        self.logger.handlers = []
        if self._file_path:
            self.logger.handlers.append(self.file_handler)
        self.logger.handlers.append(self.std_handler)

    def __getattr__(self, item):
        return getattr(self.logger, item)

    @staticmethod
    def file_handler_formatter(record, handle):
        log = "[{time}][{level}:{channel}][{filename}][{func_name}][{lineno}] {msg}".format(
            time=record.time,
            level=record.level_name,  # 日志等级
            channel=record.channel,
            filename=Path(record.filename).name,  # 文件名
            func_name=record.func_name,  # 函数名
            lineno=record.lineno,  # 行号
            msg=record.message,  # 日志内容
        )
        return log

    @property
    def file_handler(self):
        self._file_path = Path(self._file_path)
        if "." not in self._file_path.name:
            self._file_path = self._file_path.joinpath("logs/web.log")
        self._file_path.parent.mkdir(exist_ok=True)
        _log = TimedRotatingFileHandler(str(self._file_path), date_format='%Y-%m-%d', bubble=True, encoding='utf-8')
        _log.formatter = self.file_handler_formatter
        return _log

    @file_handler.setter
    def file_handler(self, file_path):
        self._file_path = file_path

    @property
    def std_handler(self):
        _log = StreamHandler(sys.stdout)
        _log.format_string = "{record.message}"
        return _log


log_instance = LogHelper(file_path=Path(__file__).parent.parent.parent)
