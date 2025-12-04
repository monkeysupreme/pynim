import sqlite3
from typing import Optional


class Database:
    def __init__(self, path: str) -> None:
        self.conn = sqlite3.connect(path)
        self.path = path

        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS database (key BLOB, value BLOB)"
        )
        self.conn.commit()

    def write(self, k: bytes, v: bytes) -> None:
        self.conn.execute(
            "INSERT INTO database (key, value) VALUES (?, ?)",
            (k, v)
        )
        self.conn.commit()

    def read(self, k: bytes) -> Optional[bytes]:
        cursor = self.conn.execute(
            "SELECT value FROM database WHERE key = ?",
            (k,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    
    def delete(self, k: bytes) -> None:
        self.conn.execute("DROP FROM database WHERE key = ?", (k,))
        self.conn.commit()
