import pathlib
from typing import Callable, Dict, List, Tuple, Union

import dataclasses

SQLITE_NAME = "LABELED_FILES.sqlite3"
VERSION = "0.3.6"


import logging

logger = logging.getLogger("exception")

formatter = logging.Formatter(
    "\n%(asctime)s - %(filename)s - %(levelname)s \n %(message)s")
log_file_handler = logging.FileHandler('exception.txt', encoding='utf-8')
log_file_handler.setFormatter(formatter)
logger.addHandler(log_file_handler)
logger.setLevel(logging.DEBUG)

logger = logging.getLogger("record")

formatter = logging.Formatter("%(asctime)s - %(filename)s: %(message)s")
log_file_handler = logging.FileHandler('record.txt', encoding='utf-8')
log_file_handler.setFormatter(formatter)
logger.addHandler(log_file_handler)
logger.setLevel(logging.INFO)


def logv(tag: str, message: str = ""):
    print(tag, message)
    logger.info(f"{tag}-{message}")


class _Setting:
    def __init__(self) -> None:
        from .sql import Connection
        self.root_path: pathlib.Path = None
        self.conn: Connection = None
        self.config: Config = None
        self.searched_tags: List[str] = []

    def connect_to(self, path: Union[str, pathlib.Path]):
        from .sql import Connection
        path = pathlib.Path(path)
        self.conn = Connection(path)

    def set_root(self, root: str):
        if self.conn:
            self.conn.close()
        self.root_path = pathlib.Path(root).absolute()
        self.connect_to(self.root_path.joinpath(SQLITE_NAME))


class Proxy:
    def __init__(self) -> None:
        self._setting: _Setting = None

    def check_init(self):
        if self._setting is None:
            self._setting = _Setting()

    def __getattr__(self, attr):
        self.check_init()
        return getattr(self._setting, attr)

    def __setattr__(self, __name: str, __value) -> None:
        if __name == "_setting":
            return super().__setattr__(__name, __value)
        self.check_init()
        return setattr(self._setting, __name, __value)


setting: _Setting = Proxy()  # singleton


@dataclasses.dataclass
class Config:
    default: str = ""
    workspaces: Dict[str, str] = dataclasses.field(default_factory=dict)
    hide_search_tag_in_result: bool = False
