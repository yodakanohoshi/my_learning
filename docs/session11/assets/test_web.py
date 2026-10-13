"""Web 版（web.py）。URL・ステータス・文言は API設計書のとおりか確かめる。

保存先はテストごとに一時ディレクトリの DB に、「今日」は固定の日付に差し替える（依存性の注入）。
"""

import re
from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from todo.sqlite_store import SqliteStore
from todo.store import TaskStore
from todo.web import app, get_store, get_today

TODAY = date(2026, 11, 1)


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    db_path = tmp_path / "test.db"

    def get_test_store() -> Iterator[TaskStore]:
        store = SqliteStore.open(db_path)
        try:
            yield store
        finally:
            store.close()

    app.dependency_overrides[get_store] = get_test_store
    app.dependency_overrides[get_today] = lambda: TODAY
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def add(client: TestClient, title: str, due: str = "") -> None:
    response = client.post("/tasks", data={"title": title, "due": due}, follow_redirects=False)
    assert response.status_code == 303


def titles(html: str) -> list[str]:
    """一覧に出ているタイトルを上から順に取り出す。"""
    return re.findall(r'<span class="title">(.*?)</span>', html)


# ---- 受け入れ条件 (1)〜(15)（docs/stories.md）。テスト名の頭の番号は条件の番号 ----


# 手順3: ここに test_1_追加すると一覧へリダイレクトし未着手で出る を書く（レッド）


# 手順5: ここに test_3_タイトルが空なら追加せずエラーを出す を書く（レッド）


# 手順6: ここに test_13_完了にすると… と test_14_ないタスクを完了にすると404 を書く（レッド）
