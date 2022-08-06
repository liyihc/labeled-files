from contextlib import contextmanager
from datetime import datetime
from inspect import cleandoc
from pathlib import Path
import sqlite3
from typing import List


from .base import BaseConnection
from ..path_types import File
from . import visit_updater


class Connection(BaseConnection):
    def init_db(self):
        from .. import setting
        with self.connect() as conn:
            conn.executescript(cleandoc(f"""
                CREATE TABLE IF NOT EXISTS file_visit(
                    file_id INTEGER PRIMARY KEY,
                    time DATETIME);
                CREATE INDEX IF NOT EXISTS file_visit_time
                    ON file_visit(time);
                CREATE TABLE IF NOT EXISTS tag_visit(
                    tag TEXT PRIMARY KEY,
                    time DATETIME);

                CREATE TABLE IF NOT EXISTS infos(
                    key VARCHAR(20) PRIMARY KEY,
                    value TEXT);
                INSERT INTO infos(key, value)
                    VALUES("version", "{setting.VERSION}");
            """))

    def update_db(self):
        with self.connect() as conn:
            visit_updater.update(conn)

    def visit_file(self, file_id: int, tags: List[str]):
        dt = str(datetime.now())
        with self.connect() as conn:
            conn.execute(
                "REPLACE INTO file_visit(file_id, time) VALUES(?,?)",
                (file_id, dt))
            conn.executemany(
                "REPLACE INTO tag_visit(tag, time) VALUES(?,?)",
                [(tag, dt) for tag in tags])

    def _get_base_time(self, sql: str, target: str):
        with self.connect() as conn:
            rets = conn.execute(sql, (target,)).fetchall()
            if not rets:
                return datetime(1970, 1, 1)
            return datetime.fromisoformat(rets[0][0])

    def get_file_time(self, file_id: int):
        return self._get_base_time(
            "SELECT time FROM file_visit WHERE file_id = ?",
            str(file_id))

    def get_tag_time(self, tag: str):
        return self._get_base_time(
            "SELECT time FROM tag_visit WHERE tag = ?",
            tag)

    def get_files_by_time(self, limit: int):
        with self.connect() as conn:
            return [
                (int(file_id), datetime.fromisoformat(time))
                for file_id, time in
                conn.execute(f"SELECT file_id, time FROM file_visit ORDER BY time DESC LIMIT {limit}")]
