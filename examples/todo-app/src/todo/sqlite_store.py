"""SQLite に保存する保存先（DB設計書）。

TaskStore（store.py）と同じメソッドを持つので、JsonStore・MemoryStore と差し替えて使える。
"""

import sqlite3
from datetime import date, datetime
from pathlib import Path

from todo.models import Task
from todo.store import TaskNotFoundError

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    due TEXT NULL,
    done INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
"""


class SqliteStore:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    @classmethod
    def open(cls, path: Path) -> "SqliteStore":
        """DB のファイルを開く。ファイルやテーブルがなければ作る。"""
        path.parent.mkdir(parents=True, exist_ok=True)
        # FastAPI は同期の依存関係を別スレッドで動かすので、作ったスレッド以外からも使えるようにする
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # 列を row["title"] のように名前で取り出せるようにする
        conn.executescript(SCHEMA)
        return cls(conn)

    def close(self) -> None:
        self.conn.close()

    def list_all(self) -> list[Task]:
        rows = self.conn.execute("SELECT id, title, due, done FROM tasks ORDER BY id").fetchall()
        return [_to_task(row) for row in rows]

    def add(self, title: str, due: date | None) -> Task:
        created_at = datetime.now().isoformat(timespec="seconds")
        # with conn: ブロックを抜けるときにコミットする（例外ならロールバック）
        with self.conn:
            cur = self.conn.execute(
                # 値は ? で渡す。SQL の文字列に埋め込まない（SQL インジェクションを防ぐ）
                "INSERT INTO tasks (title, due, created_at) VALUES (?, ?, ?)",
                (title, due.isoformat() if due else None, created_at),
            )
        assert cur.lastrowid is not None  # INSERT の直後なので必ずある
        return Task(id=cur.lastrowid, title=title, due=due)

    def mark_done(self, task_id: int) -> Task:
        with self.conn:
            cur = self.conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
        if cur.rowcount == 0:  # 更新した行がない = その id のタスクがない
            raise TaskNotFoundError(task_id)
        row = self.conn.execute(
            "SELECT id, title, due, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return _to_task(row)


def _to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        due=date.fromisoformat(row["due"]) if row["due"] else None,
        done=bool(row["done"]),
    )
