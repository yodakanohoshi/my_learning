"""TODO を管理するコマンドラインのプログラム（第6回）。

使い方:
    python todo.py add "牛乳を買う" --due 2026-11-01
    python todo.py list
    python todo.py list --overdue
    python todo.py done 3

タスクはカレントディレクトリの tasks.json に保存する。
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

TASKS_FILE = Path("tasks.json")
TITLE_MAX = 100

# タスク1件は dict で持つ: {"id": 1, "title": "牛乳を買う", "due": "2026-11-01", "done": false}
# due（期限）は JSON に日付の型がないので "YYYY-MM-DD" の文字列で保存し、期限がなければ null
type Task = dict[str, Any]


def load_tasks(path: Path) -> list[Task]:
    """保存したタスクを読む。ファイルがまだなければ空のリスト。"""
    try:
        with path.open(encoding="utf-8") as f:
            tasks: list[Task] = json.load(f)
    except FileNotFoundError:
        return []
    return tasks


def save_tasks(path: Path, tasks: list[Task]) -> None:
    # ensure_ascii=False: 日本語を "\u3042" のようなエスケープ表記にせず、そのまま書く
    with path.open("w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def parse_due(text: str) -> date:
    """--due の値を日付にする。argparse の type に渡す。"""
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"期限は YYYY-MM-DD の形で指定してください: {text}"
        ) from None


def is_overdue(task: Task, today: date) -> bool:
    """期限切れか。完了したものと、期限がないものは期限切れにならない。"""
    due = task.get("due")  # 期限のないタスクは None
    return not task["done"] and due is not None and date.fromisoformat(due) < today


def format_task(task: Task, today: date) -> str:
    if task["done"]:
        status = "完了"
    elif is_overdue(task, today):
        status = "期限切れ"
    else:
        status = "未着手"
    due = task.get("due")
    due_text = f"（期限 {due}）" if due else ""
    return f"{task['id']:>3} [{status}] {task['title']}{due_text}"


def add_task(tasks: list[Task], title: str, due: date | None) -> Task:
    title = title.strip()
    if not 1 <= len(title) <= TITLE_MAX:
        raise ValueError(f"タイトルは1〜{TITLE_MAX}文字で指定してください")
    new_id = max((t["id"] for t in tasks), default=0) + 1
    task: Task = {
        "id": new_id,
        "title": title,
        "due": due.isoformat() if due else None,
        "done": False,
    }
    tasks.append(task)
    return task


def mark_done(tasks: list[Task], task_id: int) -> Task:
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            return task
    raise KeyError(task_id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TODO を管理する")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="タスクを追加する")
    add.add_argument("title", help="タスクの内容")
    add.add_argument("--due", type=parse_due, help="期限（YYYY-MM-DD）")

    list_ = sub.add_parser("list", help="タスクの一覧を表示する")
    list_.add_argument("--overdue", action="store_true", help="期限切れだけを表示する")

    done = sub.add_parser("done", help="タスクを完了にする")
    done.add_argument("id", type=int, help="タスクの番号")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    tasks = load_tasks(TASKS_FILE)
    today = date.today()

    # どのコマンドかで処理を振り分ける（パターンマッチ）
    match args.command:
        case "add":
            try:
                task = add_task(tasks, args.title, args.due)
            except ValueError as e:
                print(e, file=sys.stderr)
                return 1
            save_tasks(TASKS_FILE, tasks)
            print(f"追加しました: {format_task(task, today)}")
        case "list":
            shown = tasks
            if args.overdue:
                shown = [t for t in tasks if is_overdue(t, today)]
            if not shown:
                print("タスクはありません")
            for task in shown:
                print(format_task(task, today))
        case "done":
            try:
                task = mark_done(tasks, args.id)
            except KeyError:
                print(f"タスクが見つかりません: {args.id}", file=sys.stderr)
                return 1
            save_tasks(TASKS_FILE, tasks)
            print(f"完了にしました: {format_task(task, today)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
