from functools import cache, cached_property
import json
import os
import pathlib
import platform
from typing import Callable, Dict, List, Tuple, Union

import dataclasses

SQLITE_FILES_NAME = "LABELED_FILES.sqlite3"
VERSION = "0.5.6"


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
        from .sql import FileConnection, VisitConnection
        self.root_path: pathlib.Path = None
        self.conn: FileConnection = None
        self.visit_conn_w: VisitConnection = []
        self.visit_conns_r: List[VisitConnection] = []
        self.config: Config = None
        self.searched_tags: List[str] = []

    def connect_to(self, path: pathlib.Path):
        from .sql import FileConnection, VisitConnection
        self.conn = FileConnection(path / SQLITE_FILES_NAME)
        self.visit_conns_r.clear()
        w_name = self.config.get_sqlite_visit_name()
        for vpath in path.glob("VISIT_TIME*.sqlite3"):
            if vpath.name != w_name:
                self.visit_conns_r.append(VisitConnection(vpath))
        self.visit_conn_w = VisitConnection(path / w_name)
        self.visit_conns_r.insert(0, self.visit_conn_w)

    def set_root(self, root: str):
        self.root_path = pathlib.Path(root).absolute()
        self.connect_to(self.root_path)

    def convert_path(self, path: pathlib.Path):
        for k, v in self.config.path_convert.items():
            if path.is_relative_to(k):
                return v / path.relative_to(k)
        return path

    @cache
    def get_clean_env(self):
        env = os.environ.copy()
        env.pop("QML2_IMPORT_PATH", None)
        env.pop("QT_PLUGIN_PATH", None)
        cwd = pathlib.Path(os.getcwd())
        paths = [path for path in env["PATH"].split(
            ';') if not pathlib.Path(path).is_relative_to(cwd)]
        env["PATH"] = ";".join(paths)
        return env


setting = Setting()


@dataclasses.dataclass
class Config:
    default: str = ""
    workspaces: Dict[str, str] = dataclasses.field(default_factory=dict)
    hide_search_tag_in_result: bool = False
    file_name_regex: bool = False
    path_mapping: Dict[str, str] = dataclasses.field(default_factory=dict)
    pc_name_override: str = ""

    @cached_property
    def path_convert(self):
        return {pathlib.Path(k): pathlib.Path(v) for k, v in self.path_mapping.items()}

    @classmethod
    def from_json(cls, s: str):
        d: dict = json.loads(s)
        d = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**d)

    def get_sqlite_visit_name(self):
        if self.pc_name_override:
            name = self.pc_name_override
        else:
            name = platform.node()
        return f"VISIT_TIME_{name}.sqlite3"
