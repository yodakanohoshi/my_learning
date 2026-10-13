"""TODO を管理するコマンドラインのプログラム（第6回の雛形）。

関数の中身（raise NotImplementedError の行）を、資料のハンズオンの手順どおりに書き換える。

使い方:
    python todo.py add "牛乳を買う"
    python todo.py list
    python todo.py done 3

タスクはカレントディレクトリの tasks.json に保存する。
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

TASKS_FILE = Path("tasks.json")
TITLE_MAX = 100

# タスク1件は dict で持つ: {"id": 1, "title": "牛乳を買う", "done": false}
type Task = dict[str, Any]


def load_tasks(path: Path) -> list[Task]:
    """保存したタスクを読む。ファイルがまだなければ空のリスト。"""
    raise NotImplementedError("手順4で書く")


def save_tasks(path: Path, tasks: list[Task]) -> None:
    raise NotImplementedError("手順4で書く")


def format_task(task: Task) -> str:
    raise NotImplementedError("手順5で書く")


def add_task(tasks: list[Task], title: str) -> Task:
    raise NotImplementedError("手順5で書く")


def mark_done(tasks: list[Task], task_id: int) -> Task:
    raise NotImplementedError("手順5で書く")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TODO を管理する")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="タスクを追加する")
    add.add_argument("title", help="タスクの内容")

    sub.add_parser("list", help="タスクの一覧を表示する")

    done = sub.add_parser("done", help="タスクを完了にする")
    done.add_argument("id", type=int, help="タスクの番号")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    tasks = load_tasks(TASKS_FILE)

    # どのコマンドかで処理を振り分ける（パターンマッチ）
    match args.command:
        case "add":
            try:
                task = add_task(tasks, args.title)
            except ValueError as e:
                print(e, file=sys.stderr)
                return 1
            save_tasks(TASKS_FILE, tasks)
            print(f"追加しました: {format_task(task)}")
        case "list":
            if not tasks:
                print("タスクはありません")
            for task in tasks:
                print(format_task(task))
        case "done":
            try:
                task = mark_done(tasks, args.id)
            except KeyError:
                print(f"タスクが見つかりません: {args.id}", file=sys.stderr)
                return 1
            save_tasks(TASKS_FILE, tasks)
            print(f"完了にしました: {format_task(task)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
