"""受講者に配る研修ディレクトリ一式を作る。

研修ディレクトリをそのままコピーし、配らないものだけを除く。
見本の TODO アプリ（examples/todo-app/ と各回終了時点の examples/todo-app-snapshots/session-NN/）は
git を使わない普通のフォルダなので、ほかの見本と同じくそのままコピーする。

- .git、仮想環境・キャッシュ、講師用（instructor.md）、作成者向け（handoff.md、docs/_template/、
  .claude/）は含めない
- HTML 版・PDF 版（docs/_build/）は含める。先に tools/ で mise run docs を実行しておく

使い方: python scripts/build_distribution.py <出力先>（出力先は空か、存在しないディレクトリ）
"""

import shutil
import sys
from pathlib import Path

from curriculum import ROOT

BUILD = ROOT / "docs" / "_build"
EXCLUDE_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".ipynb_checkpoints",
    ".vivliostyle",  # mise run docs の作業用
    "var",  # 見本のアプリを動かすとできる SQLite（var/todo.db）
    "tasks.json",  # 見本の CLI を動かすとできる保存ファイル
    "instructor.md",
}
EXCLUDE_PATHS = {
    "handoff.md",
    ".claude",
    "docs/_template",
}


def ignore(directory: str, names: list[str]) -> set[str]:
    rel = Path(directory).relative_to(ROOT)
    return {n for n in names if n in EXCLUDE_NAMES or (rel / n).as_posix() in EXCLUDE_PATHS}


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    out = Path(argv[0]).resolve()
    if out.exists() and any(out.iterdir()):
        print(f"{out} は空ではありません")
        return 1
    if out.is_relative_to(ROOT):
        print("出力先は研修ディレクトリの外にしてください")
        return 1
    if not BUILD.is_dir():
        print("注意: docs/_build/ がありません（HTML 版・PDF 版が入りません）。先に mise run docs")

    shutil.copytree(ROOT, out, ignore=ignore, dirs_exist_ok=True)

    left = [p for p in out.rglob("*") if p.name in EXCLUDE_NAMES]
    if left:
        print("除くはずのものが残っています:", *left, sep="\n")
        return 1
    print(f"{out} に配布物を作りました（.git・講師用なし）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
