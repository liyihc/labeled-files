from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import sqlite3
from typing import Iterable, Union
from inspect import cleandoc

from . import files_updater
from ..path_types import File
from .base import BaseConnection

file_types = {}


@dataclass
class PinTag:
    tag: str
    icon: bytes = ""
    rank: int = 100


class Connection(BaseConnection):
    def init_db(self):
        from .. import setting
        with self.connect() as conn:
            conn.executescript(cleandoc(f"""
                CREATE TABLE IF NOT EXISTS file_labels(
                    label TEXT,
                    file_id INTEGER,
                    PRIMARY KEY(file_id, label));
                CREATE INDEX IF NOT EXISTS file_labels_label
                    ON file_labels(label, file_id);
                CREATE TABLE IF NOT EXISTS files(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    type TEXT,
                    path TEXT,
                    ctime DATETIME,
                    vtime DATETIME,
                    icon TEXT,
                    description TEXT);
                CREATE TABLE IF NOT EXISTS pin_label(
                    label TEXT PRIMARY KEY,
                    icon TEXT,
                    rank INTEGER);
                CREATE TABLE IF NOT EXISTS infos(
                    key VARCHAR(20) PRIMARY KEY,
                    value TEXT);
                INSERT INTO infos(key, value) VALUES("version", "{setting.VERSION}");
                CREATE INDEX IF NOT EXISTS files_name
                    ON files(name);
                CREATE INDEX IF NOT EXISTS files_ctime
                    ON files(ctime);
                CREATE INDEX IF NOT EXISTS files_vtime
                    ON files(vtime); """))

    def update_db(self):
        with self.connect() as conn:
            files_updater.update(conn)

    def fetch_files(self, *args, **kwds) -> list[File]:
        """
            please use SELECT * FROM
        """
        with self.connect() as conn:
            cursor = conn.execute(*args, **kwds)
            cursor.row_factory = sqlite3.Row
            row: sqlite3.Row
            ret = []
            for row in cursor:
                ret.append(File(
                    row['id'],
                    row['name'],
                    row['type'],
                    row['path'],
                    self.fetch_file_tags(row['id']),
                    datetime.fromisoformat(row['ctime']),
                    datetime.fromisoformat(row['vtime']),
                    row['icon'],
                    row['description']))
            return ret

    def fetch_file_tags(self, file_id: int) -> list[str]:
        with self.connect() as conn:
            return [tag for tag, in conn.execute("SELECT label FROM file_labels WHERE file_id = ?", (file_id, ))]

    def insert_file(self, f: File):
        with self.connect() as conn:
            f.vtime = datetime.now()
            cur = conn.execute(
                f"INSERT INTO files(name, type, path, ctime, vtime, icon, description) VALUES(?,?,?,?,?,?,?)",
                (f.name, f.type, f.path, str(f.ctime), str(f.vtime), f.icon, f.description))
            f.id = cur.lastrowid
            self.update_file_tags(f.id, f.tags)

    def delete_file(self, file_ids: list[str]):
        if not file_ids:
            return
        with self.connect() as conn:
            ids = ",".join(str(id) for id in file_ids)
            conn.execute(f"DELETE FROM files WHERE id in ({ids})")
            conn.execute(f"DELETE FROM file_labels WHERE file_id in ({ids})")

    def update_file_tags(self, file_id: int, new_tags: Iterable[str]):
        with self.connect() as conn:
            tags = set(tag for tag, in conn.execute(
                "SELECT label FROM file_labels WHERE file_id = ?", (file_id,)))
            new_tags = set(new_tags)
            if tags != new_tags:
                conn.executemany(
                    "INSERT INTO file_labels(file_id, label) VALUES(?,?)",
                    [(file_id, tag) for tag in new_tags - tags])
                conn.executemany(
                    "DELETE FROM file_labels WHERE file_id = ? AND label = ?",
                    [(file_id, tag) for tag in tags - new_tags])

    def update_file(self, file: File):
        with self.connect() as conn:
            conn.execute(
                "UPDATE files SET name = ?, path = ?, ctime = ?, icon = ?, description = ? WHERE id = ?", (file.name, file.path, str(file.ctime), file.icon, file.description, file.id))
            self.update_file_tags(file.id, file.tags)

    def get_pin_tags(self):
        with self.connect() as conn:
            cursor = conn.execute("SELECT * FROM pin_label ORDER BY rank")
            cursor.row_factory = sqlite3.Row
            return [
                PinTag(
                    row['label'],
                    row['icon'],
                    row['rank'])
                for row in cursor
            ]

    def append_pin_tag(self, tag: str):
        if self.exist_pin_tag(tag):
            return

        with self.connect() as conn:
            max_rank = conn.execute(
                "SELECT MAX(rank) FROM pin_label").fetchall()
            if max_rank and max_rank[0][0]:
                rank = max_rank[0][0] + 1
            else:
                rank = 1
            conn.execute(
                "INSERT INTO pin_label(label, rank) VALUES(?,?)", (tag, rank))

    def remove_pin_tag(self, tag: str):
        with self.connect() as conn:
            conn.execute("DELETE FROM pin_label WHERE label = ?", (tag,))

    def exist_pin_tag(self, tag: str) -> int:
        with self.connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM pin_label WHERE label = ?", (tag,)).fetchone()[0]
