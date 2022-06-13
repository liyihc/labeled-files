from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from packaging.version import Version
import sqlite3

from . import updater
from .path_types import File

file_types = {}


@dataclass
class PinTag:
    tag: str
    icon: bytes = ""
    rank: int = 100


class Connection:
    def __init__(self, path: Path):
        exists = path.exists()
        conn = self.conn = sqlite3.connect(path)
        conn = self.conn
        if not exists:
            self.init_db()
        else:
            updater.update(conn)

    def init_db(self):
        from . import setting
        with self.conn:
            self.conn.executescript(f"""
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
    ON files(vtime); """)

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def execute(self, *args, **kwds):
        return self.conn.execute(*args, **kwds)

    def fetch_files(self, *args, **kwds) -> list[File]:
        """
            please use SELECT * FROM
        """
        cursor = self.conn.execute(*args, **kwds)
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
        return [tag for tag, in self.conn.execute("SELECT label FROM file_labels WHERE file_id = ?", (file_id, ))]

    def insert_file(self, f: File):
        with self.conn:
            f.vtime = datetime.now()
            cur = self.conn.execute(
                f"INSERT INTO files(name, type, path, ctime, vtime, icon, description) VALUES(?,?,?,?,?,?,?)",
                (f.name, f.type, f.path, str(f.ctime), str(f.vtime), f.icon, f.description))
            f.id = cur.lastrowid

    def delete_file(self, file_ids: list[str]):
        if not file_ids:
            return
        with self.conn:
            ids = ",".join(str(id) for id in file_ids)
            self.conn.execute(f"DELETE FROM files WHERE id in ({ids})")
            self.conn.execute(
                f"DELETE FROM file_labels WHERE file_id in ({ids})")

    def visit(self, file_id):
        with self.conn:
            self.conn.execute(
                "UPDATE files SET vtime = ? WHERE id = ?", (str(datetime.now()), file_id))

    def update_file(self, file: File):
        with self.conn:
            self.conn.execute(
                "UPDATE files SET name = ?, path = ?, ctime = ?, icon = ?, description = ? WHERE id = ?", (file.name, file.path, str(file.ctime), file.icon, file.description, file.id))
            tags = set(tag for tag, in self.conn.execute(
                "SELECT label FROM file_labels WHERE file_id = ?", (file.id,)))
            new_tags = set(file.tags)
            if tags != new_tags:
                self.conn.executemany(
                    "INSERT INTO file_labels(file_id, label) VALUES(?,?)",
                    [(file.id, tag) for tag in new_tags - tags])
                self.conn.executemany(
                    "DELETE FROM file_labels WHERE file_id = ? AND label = ?",
                    [(file.id, tag) for tag in tags - new_tags])

    def get_pin_tags(self):
        cursor = self.conn.execute("SELECT * FROM pin_label ORDER BY rank")
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

        max_rank = self.conn.execute(
            "SELECT MAX(rank) FROM pin_label").fetchall()
        if max_rank and max_rank[0][0]:
            rank = max_rank[0][0] + 1
        else:
            rank = 1
        with self.conn:
            self.conn.execute(
                "INSERT INTO pin_label(label, rank) VALUES(?,?)", (tag, rank))

    # def remove_pin_tags(self, tags:list[str]):
    #     if not tags:
    #         return
    #     with self.conn:
    #         self.conn.execute("DELETE FROM pin_label WHERE label in (?)", (','.join(f'"{tag}"' for tag in tags),))

    def remove_pin_tag(self, tag: str):
        with self.conn:
            self.conn.execute("DELETE FROM pin_label WHERE label = ?", (tag,))

    def exist_pin_tag(self, tag: str) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM pin_label WHERE label = ?", (tag,)).fetchone()[0]
