import pathlib
import sqlite3
from dataclasses import dataclass, field
from typing import Dict, List, Union

import pydantic
from PySide6 import QtWidgets

SQLITE_NAME = "LABELED_FILES.sqlite3"


@dataclass
class Setting:
    root_path: pathlib.Path = None
    conn: sqlite3.Connection = None
    completer: QtWidgets.QCompleter = None
    lineedits: List[QtWidgets.QLineEdit] = field(default_factory=list)

    def connect_to(self, path: Union[str, pathlib.Path]):
        conn = sqlite3.connect(path)
        with conn:
            conn.executescript("""
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
    ctime DATETIME,
    vtime DATETIME,
    description TEXT);
CREATE INDEX IF NOT EXISTS files_name
    ON files(name);
CREATE INDEX IF NOT EXISTS files_ctime
    ON files(ctime);
CREATE INDEX IF NOT EXISTS files_vtime
    ON files(vtime);
    """)
        self.conn = conn

    def set_root(self, root: str):
        if self.conn:
            self.conn.close()
        self.root_path = pathlib.Path(root)
        self.connect_to(self.root_path.joinpath(SQLITE_NAME))
        self.update_completer()

    def update_completer(self):
        self.completer = QtWidgets.QCompleter([keyword for keyword, in self.conn.execute(
            "SELECT DISTINCT label FROM file_labels")])
        for le in self.lineedits:
            le.setCompleter(self.completer)

    def get_absolute_path(self, path: Union[str, pathlib.Path]) -> pathlib.Path:
        path = pathlib.Path(path)
        if path.is_absolute():
            return path
        return self.root_path.joinpath(path)


class Config(pydantic.BaseModel):
    default: str = ""
    workspaces: Dict[str, pydantic.DirectoryPath] = {}
