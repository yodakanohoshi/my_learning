

# ---- A-04〜A-06 HTML 断片（第12回） ----


def test_一覧の断片はページ全体ではなくulだけ(client: TestClient) -> None:
    add(client, "牛乳を買う")

    response = client.get("/fragments/tasks")

    assert response.status_code == 200
    html = response.text.strip()
    assert html.startswith('<ul id="task-list">')
    assert html.endswith("</ul>")
    assert "<html" not in html
    assert titles(html) == ["牛乳を買う"]


def test_断片で追加すると追加後の一覧を返す(client: TestClient) -> None:
    add(client, "あさって", "2026-11-03")

    response = client.post("/fragments/tasks", data={"title": "あした", "due": "2026-11-02"})

    assert response.status_code == 200
    assert response.text.strip().startswith('<ul id="task-list">')
    assert titles(response.text) == ["あした", "あさって"]


def test_断片で追加して入力が正しくなければ400でエラーの断片(client: TestClient) -> None:
    response = client.post("/fragments/tasks", data={"title": " ", "due": ""})

    assert response.status_code == 400
    assert response.text.strip() == '<p class="error" role="alert">タイトルを入力してください</p>'


def test_断片で完了にすると完了後の一覧を返す(client: TestClient) -> None:
    add(client, "牛乳を買う", "2026-10-31")

    response = client.post("/fragments/tasks/1/done")

    assert response.status_code == 200
    assert response.text.strip().startswith('<ul id="task-list">')
    assert '<span class="status">完了</span>' in response.text


def test_断片でないタスクを完了にすると404でエラーの断片(client: TestClient) -> None:
    response = client.post("/fragments/tasks/99/done")

    assert response.status_code == 404
    assert response.text.strip() == '<p class="error" role="alert">タスクが見つかりません</p>'


def test_フォームに断片の送り先がある(client: TestClient) -> None:
    add(client, "牛乳を買う")

    html = client.get("/").text

    assert 'data-fragment="/fragments/tasks"' in html
    assert 'data-fragment="/fragments/tasks/1/done"' in html


def test_ページがapp_jsを読み込む(client: TestClient) -> None:
    html = client.get("/").text

    assert '<script src="/static/app.js" defer></script>' in html
    assert client.get("/static/app.js").status_code == 200
