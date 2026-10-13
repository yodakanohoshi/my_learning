"""タスクの保存先。

TaskStore（Protocol）は「保存先が持つべき振る舞い」の約束だけを書く。
JsonStore と MemoryStore は TaskStore を継承していないが、同じメソッドを持つので
TaskStore として扱える（ダックタイピング。mypy は Protocol で確かめる）。
"""

import json
from datetime import date
from pathlib import Path
from typing import Any, Protocol

from todo.models import Task


class TaskNotFoundError(LookupError):
    """指定した id のタスクがない。"""

    def __init__(self, task_id: int) -> None:
        super().__init__(f"タスクが見つかりません: {task_id}")
        self.task_id = task_id


# 手順3: ここに TaskStore（Protocol）を書く


def _next_id(tasks: list[Task]) -> int:
    return max((t.id for t in tasks), default=0) + 1


def _mark_done_in(tasks: list[Task], task_id: int) -> tuple[list[Task], Task]:
    """task_id のタスクを完了にした新しいリストと、完了にしたタスクを返す。"""
    for i, task in enumerate(tasks):
        if task.id == task_id:
            done = task.mark_done()
            return [*tasks[:i], done, *tasks[i + 1 :]], done
    raise TaskNotFoundError(task_id)


# 手順3: ここに MemoryStore を書く


class JsonStore:
    """JSON ファイルに保存する保存先。ファイルの形は第6回の tasks.json と同じ。"""

    def __init__(self, path: Path) -> None:
        self.path = path

    def list_all(self) -> list[Task]:
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return []
        return [_from_json(item) for item in json.loads(text)]

    def add(self, title: str, due: date | None) -> Task:
        tasks = self.list_all()
        task = Task(id=_next_id(tasks), title=title, due=due)
        self._save([*tasks, task])
        return task

    def mark_done(self, task_id: int) -> Task:
        tasks, done = _mark_done_in(self.list_all(), task_id)
        self._save(tasks)
        return done

    def _save(self, tasks: list[Task]) -> None:
        data = [_to_json(t) for t in tasks]
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _to_json(task: Task) -> dict[str, Any]:
    due = task.due.isoformat() if task.due else None
    return {"id": task.id, "title": task.title, "due": due, "done": task.done}


def _from_json(item: dict[str, Any]) -> Task:
    due = item.get("due")
    return Task(
        id=item["id"],
        title=item["title"],
        due=date.fromisoformat(due) if due else None,
        done=item.get("done", False),
    )
