import pathlib
from typing import Callable, Dict, List, Tuple, Union


import pydantic

SQLITE_NAME = "LABELED_FILES.sqlite3"
VERSION = "0.3.5"


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

    def connect_to(self, path: Union[str, pathlib.Path]):
        from .sql import Connection
        path = pathlib.Path(path)
        self.conn = Connection(path)

    def set_root(self, root: str):
        if self.conn:
            self.conn.close()
        self.root_path = pathlib.Path(root).absolute()
        self.connect_to(self.root_path.joinpath(SQLITE_NAME))


class Config(pydantic.BaseModel):
    default: str = ""
    workspaces: Dict[str, pydantic.DirectoryPath] = {}
