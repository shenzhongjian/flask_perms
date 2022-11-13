#!/usr/bin/env python
# @Time    : 2022/10/10 14:05
# @Author  : shen_zj
# @Email   : shenzj@keenon.com
# @File    : asyncio_help.py
# @Software: PyCharm
import asyncio
from asyncio import Task
from typing import Callable, List, Any


class AsyncioHelp(object):
    """协程处理类"""

    def __init__(self):
        self.__taskList = []  # 存放loop管理的task

    @staticmethod
    def create_task(func: Callable, *args, **kwargs) -> Task:
        task = asyncio.ensure_future(func(*args, **kwargs))
        return task

    async def gather_tasks(
            self,
            funcs: List[Callable],
            func_args: list,
            func_kwargs: list,
            return_exceptions=True
    ) -> Any:

        tasks = [self.create_task(func, *func_args[index], **func_kwargs[index]) for index, func in enumerate(funcs)]
        self.__taskList = tasks
        return await asyncio.gather(*tasks, return_exceptions=return_exceptions)

    def run(self, funcs: List[Callable], func_args: list = None, func_kwargs: list = None,
            return_exceptions=True) -> Any:
        func_args = [[]] * len(funcs) if func_args is None else func_args
        func_kwargs = [{} for _ in funcs] if func_kwargs is None else func_kwargs
        asyncio.run(self.gather_tasks(funcs, func_args, func_kwargs, return_exceptions))
        results = [t.result() for t in self.__taskList]
        results = [None if isinstance(i, Exception) else i for i in results]
        return results


