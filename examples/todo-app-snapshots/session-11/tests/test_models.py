"""タスクの状態と入力チェック（models.py）。"""

from datetime import date

import pytest

from todo.models import InvalidTaskError, Status, Task, parse_due, validate_title

TODAY = date(2026, 11, 1)


@pytest.mark.parametrize(
    ("due", "done", "expected"),
    [
        (None, False, Status.TODO),  # 期限なし
        (date(2026, 11, 2), False, Status.TODO),  # 期限は明日
        (TODAY, False, Status.TODO),  # 期限の当日はまだ期限切れではない
        (date(2026, 10, 31), False, Status.OVERDUE),  # 期限は昨日
        (date(2026, 10, 31), True, Status.DONE),  # 完了したものは期限切れにならない
        (None, True, Status.DONE),
    ],
)
def test_状態は完了と期限と今日で決まる(due: date | None, done: bool, expected: Status) -> None:
    task = Task(id=1, title="牛乳を買う", due=due, done=done)

    assert task.status(TODAY) is expected


def test_完了にすると新しいタスクを返し元のタスクは変わらない() -> None:
    task = Task(id=1, title="牛乳を買う")

    done = task.mark_done()

    assert done.done is True
    assert task.done is False
    assert done == Task(id=1, title="牛乳を買う", done=True)


def test_タイトルの前後の空白を除く() -> None:
    assert validate_title("  牛乳を買う \n") == "牛乳を買う"


@pytest.mark.parametrize("title", ["", "   "])
def test_タイトルが空ならエラー(title: str) -> None:
    with pytest.raises(InvalidTaskError, match="タイトルを入力してください"):
        validate_title(title)


def test_タイトルは100文字まで() -> None:
    assert validate_title("あ" * 100) == "あ" * 100
    with pytest.raises(InvalidTaskError, match="100文字以内"):
        validate_title("あ" * 101)


def test_期限は日付にする_空なら期限なし() -> None:
    assert parse_due("2026-11-01") == date(2026, 11, 1)
    assert parse_due("") is None
    assert parse_due("  ") is None


@pytest.mark.parametrize("text", ["2026/11/01", "2026-13-01", "あした"])
def test_期限の形が正しくなければエラー(text: str) -> None:
    with pytest.raises(InvalidTaskError, match="YYYY-MM-DD"):
        parse_due(text)
