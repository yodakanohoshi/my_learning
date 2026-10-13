"""タスク一覧を表で表示する。第4回の見本（依存パッケージ rich を使う）。"""

import sys

from rich.console import Console
from rich.table import Table

TASKS = [
    ("1", "牛乳を買う", "2026-11-01", "未着手"),
    ("2", "研修の資料を読む", "2026-10-19", "完了"),
    ("3", "歯医者を予約する", "-", "未着手"),
]


def main() -> None:
    table = Table(title="タスク一覧")
    for column in ("ID", "タイトル", "期限", "状態"):
        table.add_column(column)
    for row in TASKS:
        table.add_row(*row)

    console = Console()
    console.print(table)
    console.print(f"Python {sys.version.split()[0]} ({sys.executable})")


if __name__ == "__main__":
    main()
