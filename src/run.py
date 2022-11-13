from pathlib import Path
import sys

from config.base_config import BaseConfig
from src import create_app

sys.path.insert(0, str(Path.cwd()))

app = create_app(BaseConfig)
print(app.url_map)


if __name__ == '__main__':
    app.run(host='0.0.0.0')

