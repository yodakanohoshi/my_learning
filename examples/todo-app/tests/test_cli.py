"""コマンドライン（cli.py）。保存先は MemoryStore、「今日」は固定して動かす。"""

from datetime import date
from pathlib import Path

import pytest

from todo.cli import main
from todo.models import Task
from todo.store import MemoryStore

TODAY = date(2026, 11, 1)


@pytest.fixture
def store() -> MemoryStore:
    return MemoryStore(
        [
            Task(id=1, title="レポートを出す", due=date(2026, 11, 5)),
            Task(id=2, title="牛乳を買う", due=date(2026, 10, 30)),
            Task(id=3, title="本を返す"),
        ]
    )


def run(store: MemoryStore, *argv: str) -> int:
    return main(list(argv), store=store, today=TODAY)


def test_addで追加する(store: MemoryStore, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(store, "add", "  傘を買う ", "--due", "2026-11-02") == 0

    assert store.list_all()[-1] == Task(id=4, title="傘を買う", due=date(2026, 11, 2))
    assert "追加しました:   4 [未着手] 傘を買う（期限 2026-11-02）" in capsys.readouterr().out


def test_addで期限の形が正しくなければ終了コード1(
    store: MemoryStore, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(store, "add", "傘を買う", "--due", "11/2") == 1

    assert "YYYY-MM-DD" in capsys.readouterr().err
    assert len(store.list_all()) == 3


def test_listは期限が近い順に表示する(
    store: MemoryStore, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(store, "list") == 0

    assert capsys.readouterr().out.splitlines() == [
        "  2 [期限切れ] 牛乳を買う（期限 2026-10-30）",
        "  1 [未着手] レポートを出す（期限 2026-11-05）",
        "  3 [未着手] 本を返す",
    ]


def test_list_overdueは期限切れだけを表示する(
    store: MemoryStore, capsys: pytest.CaptureFixture[str]
) -> None:
    run(store, "list", "--overdue")

    assert capsys.readouterr().out.splitlines() == ["  2 [期限切れ] 牛乳を買う（期限 2026-10-30）"]


def test_doneで完了にすると期限切れでなくなる(
    store: MemoryStore, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(store, "done", "2") == 0
    run(store, "list", "--overdue")

    assert capsys.readouterr().out.splitlines()[-1] == "タスクはありません"


def test_doneでない番号なら終了コード1(
    store: MemoryStore, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(store, "done", "9") == 1

    assert "タスクが見つかりません: 9" in capsys.readouterr().err


def test_保存先を渡さなければカレントディレクトリのtasks_jsonに保存する(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    main(["add", "牛乳を買う"])

    assert '"title": "牛乳を買う"' in (tmp_path / "tasks.json").read_text(encoding="utf-8")
