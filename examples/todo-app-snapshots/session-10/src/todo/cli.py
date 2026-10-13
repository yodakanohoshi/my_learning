"""コマンドラインの入口（uv run todo ...）。

使い方:
    uv run todo add "牛乳を買う" --due 2026-11-01
    uv run todo list
    uv run todo list --overdue
    uv run todo done 3
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from todo.models import (
    InvalidTaskError,
    Status,
    Task,
    parse_due,
    sort_by_due,
    validate_title,
)
from todo.store import JsonStore, TaskNotFoundError, TaskStore

TASKS_FILE = Path("tasks.json")


def format_task(task: Task, today: date) -> str:
    due = f"（期限 {task.due.isoformat()}）" if task.due else ""
    return f"{task.id:>3} [{task.status(today).value}] {task.title}{due}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo", description="TODO を管理する")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="タスクを追加する")
    add.add_argument("title", help="タスクの内容（1〜100文字）")
    add.add_argument("--due", default="", help="期限（YYYY-MM-DD）")

    list_ = sub.add_parser("list", help="タスクの一覧を表示する")
    list_.add_argument("--overdue", action="store_true", help="期限切れだけを表示する")

    done = sub.add_parser("done", help="タスクを完了にする")
    done.add_argument("id", type=int, help="タスクの番号")
    return parser


def run_add(store: TaskStore, today: date, title: str, due: str) -> None:
    task = store.add(validate_title(title), parse_due(due))
    print(f"追加しました: {format_task(task, today)}")


def run_list(store: TaskStore, today: date, overdue_only: bool) -> None:
    tasks = sort_by_due(store.list_all())
    if overdue_only:
        tasks = [t for t in tasks if t.status(today) is Status.OVERDUE]
    if not tasks:
        print("タスクはありません")
        return  # 早期 return: 以降は「タスクがある」ときだけ考えればよい
    for task in tasks:
        print(format_task(task, today))


def run_done(store: TaskStore, today: date, task_id: int) -> None:
    task = store.mark_done(task_id)
    print(f"完了にしました: {format_task(task, today)}")


def main(
    argv: list[str] | None = None,
    store: TaskStore | None = None,
    today: date | None = None,
) -> int:
    """終了コード（0: 成功、1: 入力の誤りなど）を返す。

    store と today を引数で渡せるようにしておくと、保存先や「今日」を差し替えて動かせる。
    """
    args = build_parser().parse_args(argv)
    store = store if store is not None else JsonStore(TASKS_FILE)
    today = today if today is not None else date.today()

    try:
        match args.command:
            case "add":
                run_add(store, today, args.title, args.due)
            case "list":
                run_list(store, today, args.overdue)
            case "done":
                run_done(store, today, args.id)
    except (InvalidTaskError, TaskNotFoundError) as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
