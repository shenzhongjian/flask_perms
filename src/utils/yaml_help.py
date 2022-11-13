from pathlib import Path
from threading import Lock
from typing import Any

import yaml


class SiteYaml:
    """基于Yaml的配置类"""

    def __init__(self, config_path: str):
        """
        :param config_path:  配置文件路径
        """
        self.config_path = config_path
        self.mutex = Lock()

    def get_config(self, key: str = None, default: Any = None) -> Any:
        """
        返回配置项的值，如果配置不存在，返回default.
        :param key: 配置名称
        :param default: 默认返回值
        :return:
        """

        with self.mutex:
            setting = default
            if (file_path := Path(self.config_path)).exists():
                config_settings = yaml.load(file_path.read_text(), Loader=yaml.FullLoader)
                setting = config_settings.get(key, default) if key is not None else config_settings

        return setting

    def update_config(self, settings: dict):
        """
        更新本地yaml配置文件
        :param settings: 最新配置内容
        :return:
        """
        with self.mutex:
            if not (f := Path(self.config_path)).exists():
                f.touch(exist_ok=True)
            yaml.dump(settings, f.open('w'), allow_unicode=True, indent=4, default_flow_style=False)


