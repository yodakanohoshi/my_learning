"""保存先（store.py・sqlite_store.py）。

同じテストを MemoryStore・JsonStore・SqliteStore で動かす。どちらも TaskStore の約束を
守っていれば、同じテストが通る。
"""

from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest

from todo.models import Task
from todo.sqlite_store import SqliteStore
from todo.store import JsonStore, MemoryStore, TaskNotFoundError, TaskStore


@pytest.fixture(params=["memory", "json", "sqlite"])
def store(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[TaskStore]:
    """params の数だけ、このフィクスチャを使うテストが繰り返し動く。"""
    match request.param:
        case "memory":
            yield MemoryStore()
        case "json":
            yield JsonStore(tmp_path / "tasks.json")
        case "sqlite":
            sqlite_store = SqliteStore.open(tmp_path / "test.db")
            yield sqlite_store
            sqlite_store.close()
        case _:
            raise ValueError(request.param)


def test_最初は空(store: TaskStore) -> None:
    assert store.list_all() == []


def test_追加すると1から順に番号が付く(store: TaskStore) -> None:
    first = store.add("牛乳を買う", date(2026, 11, 1))
    second = store.add("レポートを出す", None)

    assert first == Task(id=1, title="牛乳を買う", due=date(2026, 11, 1))
    assert second.id == 2
    assert store.list_all() == [first, second]


def test_完了にすると保存される(store: TaskStore) -> None:
    store.add("牛乳を買う", None)
    store.add("レポートを出す", None)

    done = store.mark_done(2)

    assert done.done is True
    assert [t.done for t in store.list_all()] == [False, True]


def test_ない番号を完了にするとエラー(store: TaskStore) -> None:
    with pytest.raises(TaskNotFoundError, match="タスクが見つかりません: 9"):
        store.mark_done(9)


def test_JsonStoreは別のインスタンスからも読める(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    JsonStore(path).add("牛乳を買う", date(2026, 11, 1))

    assert JsonStore(path).list_all() == [Task(id=1, title="牛乳を買う", due=date(2026, 11, 1))]


def test_JsonStoreは第6回のtasks_jsonを読める(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    path.write_text(
        '[{"id": 1, "title": "牛乳を買う", "due": null, "done": true}]', encoding="utf-8"
    )

    assert JsonStore(path).list_all() == [Task(id=1, title="牛乳を買う", done=True)]


def test_SqliteStoreは開き直しても読める(tmp_path: Path) -> None:
    path = tmp_path / "test.db"
    first = SqliteStore.open(path)
    first.add("牛乳を買う", date(2026, 11, 1))
    first.close()

    second = SqliteStore.open(path)
    tasks = second.list_all()
    created_at = second.conn.execute("SELECT created_at FROM tasks").fetchone()[0]
    second.close()

    assert tasks == [Task(id=1, title="牛乳を買う", due=date(2026, 11, 1))]
    assert created_at  # 追加した日時が入る
