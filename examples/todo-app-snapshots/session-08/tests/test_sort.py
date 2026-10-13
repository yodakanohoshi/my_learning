"""期限が近い順に並べる（第8回に TDD で足した機能）。"""

from datetime import date

from todo.models import Task, sort_by_due


def ids(tasks: list[Task]) -> list[int]:
    return [t.id for t in tasks]


def test_期限が近い順に並べる() -> None:
    tasks = [
        Task(id=1, title="a", due=date(2026, 11, 3)),
        Task(id=2, title="b", due=date(2026, 11, 1)),
        Task(id=3, title="c", due=date(2026, 11, 2)),
    ]

    assert ids(sort_by_due(tasks)) == [2, 3, 1]


def test_期限なしは最後に並べる() -> None:
    tasks = [
        Task(id=1, title="a"),
        Task(id=2, title="b", due=date(2026, 12, 31)),
    ]

    assert ids(sort_by_due(tasks)) == [2, 1]


def test_期限が同じなら番号の順() -> None:
    tasks = [
        Task(id=3, title="c", due=date(2026, 11, 1)),
        Task(id=1, title="a", due=date(2026, 11, 1)),
        Task(id=4, title="d"),
        Task(id=2, title="b"),
    ]

    assert ids(sort_by_due(tasks)) == [1, 3, 2, 4]


def test_元のリストは変えない() -> None:
    tasks = [Task(id=2, title="b", due=date(2026, 11, 2)), Task(id=1, title="a")]

    sort_by_due(tasks)

    assert ids(tasks) == [2, 1]
