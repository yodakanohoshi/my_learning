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


def test_1_追加すると一覧へリダイレクトし未着手で出る(client: TestClient) -> None:
    response = client.post("/tasks", data={"title": "牛乳を買う", "due": "2026-11-01"})

    assert response.status_code == 200  # リダイレクトの先（GET /）
    assert response.url.path == "/"
    assert titles(response.text) == ["牛乳を買う"]
    assert '<span class="status">未着手</span>' in response.text


def test_1_期限は空でも追加できる(client: TestClient) -> None:
    add(client, "牛乳を買う", "")

    assert titles(client.get("/").text) == ["牛乳を買う"]


def test_2_タイトルの前後の空白は除いて保存する(client: TestClient) -> None:
    add(client, "  牛乳を買う \t")

    assert titles(client.get("/").text) == ["牛乳を買う"]


@pytest.mark.parametrize("title", ["", "   "])
def test_3_タイトルが空なら追加せずエラーを出す(client: TestClient, title: str) -> None:
    response = client.post("/tasks", data={"title": title, "due": ""})

    assert response.status_code == 400
    assert '<p class="error" role="alert">タイトルを入力してください</p>' in response.text
    assert "タスクはありません" in response.text


def test_4_タイトルが101文字以上なら追加せずエラーを出す(client: TestClient) -> None:
    response = client.post("/tasks", data={"title": "あ" * 101, "due": ""})

    assert response.status_code == 400
    assert "タイトルは100文字以内で入力してください" in response.text
    assert "タスクはありません" in response.text


def test_4_タイトルは100文字ちょうどなら追加できる(client: TestClient) -> None:
    add(client, "あ" * 100)

    assert titles(client.get("/").text) == ["あ" * 100]


def test_5_期限が日付の形でなければ追加せずエラーを出す(client: TestClient) -> None:
    response = client.post("/tasks", data={"title": "牛乳を買う", "due": "11/5"})

    assert response.status_code == 400
    assert "期限は YYYY-MM-DD の形で入力してください" in response.text
    assert "タスクはありません" in response.text


def test_6_入力エラーのとき入れた値はフォームに残る(client: TestClient) -> None:
    response = client.post("/tasks", data={"title": "牛乳を買う", "due": "11/5"})

    assert 'name="title" value="牛乳を買う"' in response.text
    assert 'name="due" value="11/5"' in response.text


def test_7_一覧は期限が近い順で期限なしは最後(client: TestClient) -> None:
    add(client, "期限なし")
    add(client, "あさって", "2026-11-03")
    add(client, "あした", "2026-11-02")
    add(client, "あした2", "2026-11-02")

    assert titles(client.get("/").text) == ["あした", "あした2", "あさって", "期限なし"]


def test_8_一覧にタイトルと期限と状態が出る(client: TestClient) -> None:
    add(client, "牛乳を買う", "2026-11-05")

    html = client.get("/").text

    assert '<span class="title">牛乳を買う</span>' in html
    assert '<span class="due">2026-11-05</span>' in html
    assert '<span class="status">未着手</span>' in html


def test_9_期限の当日はまだ期限切れではなく翌日以降は期限切れ(client: TestClient) -> None:
    add(client, "昨日まで", "2026-10-31")
    add(client, "今日まで", "2026-11-01")  # TODAY

    html = client.get("/").text

    assert re.search(r'class="task status-overdue">\s*<span class="title">昨日まで', html)
    assert re.search(r'class="task status-todo">\s*<span class="title">今日まで', html)
    assert '<span class="status">期限切れ</span>' in html  # 色だけでなく文字でも出る


def test_10_タイトルの記号は文字のまま出る(client: TestClient) -> None:
    add(client, "<script>alert(1)</script>")

    html = client.get("/").text

    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<script>alert(1)" not in html


def test_11_タスクがなければタスクはありませんと出る(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert '<ul id="task-list">' in response.text
    assert "タスクはありません" in response.text


def test_12_完了ボタンは未完了のタスクにだけ出る(client: TestClient) -> None:
    add(client, "牛乳を買う")
    add(client, "本を返す")
    client.post("/tasks/1/done")

    html = client.get("/").text

    assert 'action="/tasks/1/done"' not in html
    assert 'action="/tasks/2/done"' in html


def test_13_完了にすると一覧へリダイレクトし期限切れだったものも完了と出る(
    client: TestClient,
) -> None:
    add(client, "牛乳を買う", "2026-10-31")

    response = client.post("/tasks/1/done", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    html = client.get("/").text
    assert '<span class="status">完了</span>' in html
    assert "期限切れ</span>" not in html


def test_14_ないタスクを完了にすると404(client: TestClient) -> None:
    response = client.post("/tasks/99/done")

    assert response.status_code == 404
    assert '<p class="error" role="alert">タスクが見つかりません</p>' in response.text


def test_15_overdue_1で期限切れだけが出てリンクで切り替えられる(client: TestClient) -> None:
    add(client, "牛乳を買う", "2026-10-31")
    add(client, "レポートを出す", "2026-11-01")
    add(client, "本を読む")

    page = client.get("/?overdue=1").text

    assert titles(page) == ["牛乳を買う"]
    assert '<a href="/?overdue=1" aria-current="page">期限切れだけ</a>' in page
    assert '<a href="/">すべて</a>' in page
    assert len(titles(client.get("/").text)) == 3
    assert len(titles(client.get("/?overdue=0").text)) == 3  # 1 以外はすべて


# ---- 設計レビューで決めたこと（API設計書 6章） ----


def test_完了済みをもう一度完了にしてもエラーにしない(client: TestClient) -> None:
    add(client, "牛乳を買う")
    client.post("/tasks/1/done")

    response = client.post("/tasks/1/done", follow_redirects=False)

    assert response.status_code == 303


# ---- 設定 ----


def test_DBの場所は環境変数TODO_DB_PATHで決まる(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "sub" / "todo.db"
    monkeypatch.setenv("TODO_DB_PATH", str(db_path))
    app.dependency_overrides[get_today] = lambda: TODAY
    with TestClient(app) as client:
        add(client, "牛乳を買う")
    app.dependency_overrides.clear()

    assert db_path.exists()
