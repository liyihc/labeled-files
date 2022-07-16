from functools import cached_property
import pathlib
from typing import Callable, Dict, List, Tuple, Union

import dataclasses

SQLITE_NAME = "LABELED_FILES.sqlite3"
VERSION = "0.4.0"


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


class Setting:
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

    def convert_path(self, path: pathlib.Path):
        for k, v in self.config.path_converts.items():
            if path.is_relative_to(k):
                return v / path.relative_to(k)
        return path


setting = Setting()


@dataclasses.dataclass
class Config:
    default: str = ""
    workspaces: Dict[str, str] = dataclasses.field(default_factory=dict)
    hide_search_tag_in_result: bool = False
    alternative_paths: List[List[str]] = dataclasses.field(
        default_factory=list)

    @cached_property
    def path_converts(self):
        ret: Dict[pathlib.Path, pathlib.Path] = {}
        for paths in self.alternative_paths:
            for path in paths:
                tmp = pathlib.Path(path)
                if tmp.exists():
                    ret.update({pathlib.Path(p): tmp for p in paths})
                    break
            else:
                pass  # show info that cannot find a exist path for paths
        return ret

