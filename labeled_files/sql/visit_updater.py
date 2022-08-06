import sqlite3
from typing import Callable, List, Tuple


from packaging.version import Version

updaters: List[Tuple[Version, Callable[[sqlite3.Connection], None]]] = []


def Register(ver: Version):
    def decorator(func):
        updaters.append((ver, func))
    return decorator

def update(conn:sqlite3.Connection):
    updaters.sort(key=lambda v:v[0])
    version = conn.execute(
        'SELECT value FROM infos WHERE key = "version"'
    ).fetchone()[0]
    version = Version(version)

    if not updaters or updaters[-1][0] <=version:
        return
    for ver, updater in updaters:
        if ver>version:
            with conn:
                updater(conn)