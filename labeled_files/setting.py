import pathlib
import sqlite3
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple, Union
from packaging.version import Version


import pydantic

SQLITE_NAME = "LABELED_FILES.sqlite3"
VERSION = "0.2.0"

updaters: List[Tuple[Version, Callable[[sqlite3.Connection], None]]] = []


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


@dataclass
class Setting:
    root_path: pathlib.Path = None
    conn: sqlite3.Connection = None

    def connect_to(self, path: Union[str, pathlib.Path]):
        path = pathlib.Path(path)
        exists = path.exists()
        conn = sqlite3.connect(path)
        self.conn = conn
        if not exists:
            with conn:
                conn.executescript(f"""
CREATE TABLE IF NOT EXISTS file_labels(
    label TEXT,
    file_id INTEGER,
    PRIMARY KEY(file_id, label));
CREATE INDEX IF NOT EXISTS file_labels_label
    ON file_labels(label, file_id);
CREATE TABLE IF NOT EXISTS files(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    path TEXT,
    is_dir BOOLEAN,
    ctime DATETIME,
    vtime DATETIME,
    icon TEXT,
    description TEXT);
CREATE TABLE IF NOT EXISTS infos(
    key VARCHAR(20) PRIMARY KEY,
    value TEXT);
INSERT INTO infos(key, value) VALUES("version", "{VERSION}");
CREATE INDEX IF NOT EXISTS files_name
    ON files(name);
CREATE INDEX IF NOT EXISTS files_ctime
    ON files(ctime);
CREATE INDEX IF NOT EXISTS files_vtime
    ON files(vtime); """)
        else:
            if list(conn.execute('SELECT * FROM sqlite_master WHERE name = "infos"')):
                version = conn.execute(
                    'SELECT value FROM infos WHERE key = "version"').fetchone()[0]
            else:
                version = "0.0.0"
            version = Version(version)
            if not updaters or updaters[-1][0] <= version:
                return
            for ver, updater in updaters:
                if ver > version:
                    updater(conn)

    def set_root(self, root: str):
        if self.conn:
            self.conn.close()
        self.root_path = pathlib.Path(root)
        self.connect_to(self.root_path.joinpath(SQLITE_NAME))

    def get_absolute_path(self, path: Union[str, pathlib.Path]) -> pathlib.Path:
        path = pathlib.Path(path)
        if path.is_absolute():
            return path
        return self.root_path.joinpath(path)


class Config(pydantic.BaseModel):
    default: str = ""
    workspaces: Dict[str, pydantic.DirectoryPath] = {}


def updater_0_1_1(conn: sqlite3.Connection):
    conn.executescript(f"""
CREATE TABLE IF NOT EXISTS infos(
    key VARCHAR(20) PRIMARY KEY,
    value TEXT);
INSERT INTO infos(key, value) VALUES("version", "{VERSION}");
ALTER TABLE files ADD COLUMN icon TEXT;
""")


updaters.append((Version("0.1.1"), updater_0_1_1))
