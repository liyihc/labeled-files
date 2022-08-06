
import sqlite3
from typing import Callable, List, Tuple

from packaging.version import Version

updaters: List[Tuple[Version, Callable[[sqlite3.Connection], None]]] = []


def Register(ver: Version):
    def decorator(func):
        updaters.append((ver, func))
    return decorator


@Register(Version("0.1.1"))
def update_to_0_1_1(conn: sqlite3.Connection):
    conn.executescript(f"""
CREATE TABLE IF NOT EXISTS infos(
    key VARCHAR(20) PRIMARY KEY,
    value TEXT);
INSERT INTO infos(key, value) VALUES("version", "0.1.1");
ALTER TABLE files ADD COLUMN icon TEXT;
""")


@Register(Version("0.3.0"))
def update_to_0_3_0(conn: sqlite3.Connection):
    conn.executescript(f"""
DROP INDEX IF EXISTS files_name;
DROP INDEX IF EXISTS files_ctime;
DROP INDEX IF EXISTS files_vtime;
ALTER TABLE files RENAME TO files_v_0_1_1;

CREATE TABLE files(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT,
    type TEXT,
    path TEXT,
    ctime DATETIME,
    vtime DATETIME,
    icon TEXT,
    description TEXT);
CREATE INDEX files_name ON files(name);
CREATE INDEX files_ctime ON files(ctime);
CREATE INDEX files_vtime ON files(vtime); """)
    files = []
    for id, name, path, is_dir, ctime, vtime, icon, desc in conn.execute("SELECT id, name, path, is_dir, ctime, vtime, icon, description FROM files_v_0_1_1"):
        typ = 'folder' if is_dir else 'file'
        files.append((id, name, typ, path, ctime, vtime, icon, desc))
    conn.executemany("INSERT INTO files VALUES(?,?,?,?,?,?,?,?)", files)
    conn.execute('UPDATE infos SET value = "0.3.0" WHERE key = "version"')


@Register(Version("0.3.3"))
def update_to_0_3_3(conn: sqlite3.Connection):
    conn.execute("""
CREATE TABLE IF NOT EXISTS pin_label(
    label TEXT PRIMARY KEY,
    icon TEXT,
    rank INTEGER);
    """)
    conn.execute('UPDATE infos SET value = "0.3.3" WHERE key = "version"')


def update(conn: sqlite3.Connection):
    updaters.sort(key=lambda v: v[0])

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
            with conn:
                updater(conn)
