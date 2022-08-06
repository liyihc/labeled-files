from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
import sqlite3
from weakref import  ReferenceType, ref
from typing import List
from PySide6.QtCore import QTimer

connections:List[ReferenceType['BaseConnection']] = []

class BaseConnection(ABC):
    def __init__(self, path: Path) -> None:
        self.path = path
        self._conn: sqlite3.Connection | None = None
        self._timer = QTimer()
        self._timer.timeout.connect(self.close_db)
        if not path.exists():
            self.init_db()
        else:
            self.update_db()
        connections.append(ref(self))

    @contextmanager
    def connect(self):
        if self._conn:
            yield self._conn
            if self._timer.isActive():
                self._timer.stop()
                self._timer.start(10 * 1000)
        else:
            conn = self._conn = sqlite3.connect(self.path)
            print("db connect", self.path)
            with conn:
                yield conn
            self._timer.start(10 * 1000)


    def close_db(self):
        if self._conn:
            print("db close", self.path)
            self._conn.commit()
            self._conn.close()
            self._conn = None
    
    def __del__(self):
        self.close_db()

    
    def execute(self, *args, **kwds):
        assert self._conn is not None, "execute should be called in a context manager"
        return self._conn.execute(*args, **kwds)
    
    @abstractmethod
    def update_db(self):
        pass

    @abstractmethod
    def init_db(self):
        pass

def on_close():
    for conn_ref in connections:
        conn = conn_ref()
        if conn is not None:
            if conn._timer.isActive():
                conn._timer.stop()
            conn.close_db()