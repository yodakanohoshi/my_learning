"""タスクと、その状態の決まり。保存先や画面には依存しない。"""

from dataclasses import dataclass, replace
from datetime import date
from enum import Enum

TITLE_MAX = 100


class Status(Enum):
    TODO = "未着手"
    DONE = "完了"
    OVERDUE = "期限切れ"  # 完了していない・期限が今日より前


class InvalidTaskError(ValueError):
    """入力が正しくない。メッセージはそのまま利用者に見せる。"""


@dataclass(frozen=True)
class Task:
    """タスク1件。frozen=True なので作った後は変えられない（変えるときは新しく作る）。"""

    id: int
    title: str
    due: date | None = None
    done: bool = False

    def status(self, today: date) -> Status:
        if self.done:
            return Status.DONE  # 完了したものは期限切れにならない
        if self.due is not None and self.due < today:
            return Status.OVERDUE
        return Status.TODO

    def mark_done(self) -> "Task":
        """完了にしたタスクを返す（自分自身は変えない）。"""
        return replace(self, done=True)


def validate_title(raw: str) -> str:
    """前後の空白を除いたタイトルを返す。1〜100文字でなければ InvalidTaskError。"""
    title = raw.strip()
    if not title:
        raise InvalidTaskError("タイトルを入力してください")
    if len(title) > TITLE_MAX:
        raise InvalidTaskError(f"タイトルは{TITLE_MAX}文字以内で入力してください")
    return title


def parse_due(raw: str) -> date | None:
    """期限の文字列（YYYY-MM-DD）を日付にする。空なら期限なし（None）。"""
    raw = raw.strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise InvalidTaskError("期限は YYYY-MM-DD の形で入力してください") from None
