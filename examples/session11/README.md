# 第11回 見本

[第11回の資料](../../docs/session11/README.md) の成果物「Web 版＋受け入れ条件 (1)〜(15) のテスト」の見本は [`todo-app-snapshots/session-11/`](../todo-app-snapshots/session-11/) です。第10回の設計書（[`session-10/`](../todo-app-snapshots/session-10/)）のとおりに、テストを先に書いてから Web 版にしました。画面は素の HTML フォームの送信とリダイレクトです。

## 第10回から変わったもの

| 種類 | ファイル | ハンズオンの手順 |
| --- | --- | --- |
| 設定 | `pyproject.toml` に FastAPI・Jinja2・uvicorn・python-multipart・httpx2、`mise.toml` に `TODO_DB_PATH` と `dev`・`db-reset` のタスク、`.gitignore` に `var/`・`.env` | 1 |
| 保存先 | `src/todo/sqlite_store.py`（`SqliteStore.open`・`close`、`TaskStore` の約束を満たす）、`tests/test_store.py`（同じテストに `"sqlite"` を足し、開き直しのテストを足した） | 2 |
| 画面 | `src/todo/web.py`（依存関係 `get_store`・`get_today` と `StoreDep`・`TodayDep`、`render_index`、`index`・`add_task`・`mark_done`）、`src/todo/templates/`（`base.html`・`index.html`）、`src/todo/static/style.css` | 3〜6 |
| テスト | `tests/test_web.py`（TestClient。テスト名の頭の番号は受け入れ条件の番号） | 3・5・6（手で書く）、7（コピー） |
| 文書 | `README.md`（Web 版の使い方・コードの構成）、`docs/stories.md`（受け入れ条件にチェック。設計書の中身は変わっていない） | 9 |

Issue #15 はこの作業のタスクで、PR #16 で #15 とストーリーの Issue #8〜#11 を閉じます。

ハンズオンでは、素材の [`docs/session11/assets/`](../../docs/session11/assets/) を使います。`web.py` と `test_web.py` は、この見本から受講者が手で書く部分を抜いたもの（「手順N: ここに …」のコメント）、`test_web_rest.py` は手順7で `test_web.py` の末尾に足す残りのテストです。そのため受講者の `test_web.py` は、テストの中身は見本と同じで、並び順だけが違います。

## 見方

```sh
cd ~/handsoff/examples/todo-app-snapshots
diff -rq session-10 session-11
diff -u session-10/tests/test_store.py session-11/tests/test_store.py   # 保存先を1つ足すだけで同じテストが動く
cd session-11
mise trust && mise install && mise run setup
mise run check
mise run dev        # http://127.0.0.1:8000 。止めるときは Ctrl+C
```

| 順 | テスト（`tests/test_web.py`） | 実装 | ハンズオンの手順 |
| --- | --- | --- | --- |
| 1 | `test_1_追加すると…` | `web.py` の `add_task`（最小）、`templates/` | 3・4 |
| 2 | `test_3_タイトルが空なら…` | `add_task` で `InvalidTaskError` を 400 に | 5 |
| 3 | `test_13_…`・`test_14_…`（完了・404） | `web.py` の `mark_done`、`sqlite_store.py` の `mark_done` | 6 |
| 4 | 残りの (1)〜(15)、再完了、`TODO_DB_PATH` | （実装は変えない。並べ替えと状態は第8回までの `sort_by_due`・`Task.status`） | 7 |

- テスト用の DB と「今日」は、`client` フィクスチャで `app.dependency_overrides` に差し替えている
- テストを先に書いた順序（レッド → グリーン）はフォルダには残っていません。上の表の順にテストと実装を並べて読んでください

追いつくときは [examples/README.md](../README.md#遅れた人が追いつく方法) の手順で、フォルダ名を `session-11` にします。この時点では、第12回の演習で見つける不具合はまだ作り込まれていません（部分更新を足したときに出る）。
