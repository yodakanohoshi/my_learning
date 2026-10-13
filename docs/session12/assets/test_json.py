

# ---- A-07 比較用の JSON ----


def test_JSONで完了にするとidとdoneを返す(client: TestClient) -> None:
    add(client, "牛乳を買う")

    response = client.post("/api/tasks/1/done")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "done": True}
    assert '<span class="status">完了</span>' in client.get("/").text


def test_JSONでないタスクを完了にすると404(client: TestClient) -> None:
    response = client.post("/api/tasks/99/done")

    assert response.status_code == 404
    assert response.json() == {"detail": "タスクが見つかりません"}
