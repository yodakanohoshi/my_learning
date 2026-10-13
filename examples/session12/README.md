# 第12回 見本

[第12回の資料](../../docs/session12/README.md) の成果物「fetch による部分更新（HTML 断片＋比較用の JSON 版）＋不具合票 BUG-001 とその修正＋発表資料」の見本は [`todo-app-snapshots/session-12/`](../todo-app-snapshots/session-12/) です。最新の [`todo-app/`](../todo-app/) と同じ状態です。第11回の終わり（[`session-11/`](../todo-app-snapshots/session-11/)。素の HTML フォームとリダイレクト）を、fetch による部分更新に書き換えました。フォームの `action` は残してあるので、JavaScript がなくても第11回と同じように動きます。

## 第11回から変わったもの

| 種類 | ファイル | ハンズオンの手順 |
| --- | --- | --- |
| テンプレート | 一覧を `_task_list.html` に切り出し、エラーの断片 `_error.html` を足した。`index.html` のフォームに `data-fragment`（fetch の送り先）、エラー表示欄を `<div id="error-area">` に。`base.html` で `app.js` を読み込む | 1 |
| サーバ | `src/todo/web.py` に断片の URL の節（`render_task_list`・`render_error`、`GET /fragments/tasks`、`POST /fragments/tasks`、`POST /fragments/tasks/{id}/done`）と、比較用の `POST /api/tasks/{id}/done`（JSON） | 1・3 |
| JavaScript | `src/todo/static/app.js`（`document` で submit を受け、`data-fragment` の URL へ fetch。返った HTML 断片で `#task-list` を差し替え、エラーは `#error-area` に入れる）、`src/todo/static/done-json.js`（比較用: 完了だけ JSON で受け取り、DOM を自分で書き換える。既定では読み込まない） | 1〜3 |
| テスト | `tests/test_web.py` に断片・app.js の読み込み・JSON・BUG-001 のテスト（第11回のテストは変えていない） | 1・3・5 |
| 設計書 | `docs/design/api.md`（1.1: A-04〜A-07、`data-fragment`、fetch と JSON のシーケンス図、7章 HTML 断片と JSON の比較）、`docs/design/architecture.md`（1.1: ブラウザの JavaScript） | 4 |
| 不具合票 | `docs/bugs/BUG-001.md`（期限切れだけを表示中に完了すると、全部のタスクが表示される）。修正は `web.py` の `overdue_query` と、テンプレートの `data-fragment` の `{{ query }}` | 5 |
| 発表資料 | `docs/presentation.md`（4節: 何を作ったか → システム構成 → デモ手順 → 設計とテストの工夫1つ。1節に作った記録の数字） | 6 |
| 文書 | `README.md`（部分更新・比較用の JSON 版・`docs/bugs/`・発表資料） | 5 |

Issue #17（部分更新）を PR #18 で、不具合の Issue #19 を PR #20 で、Issue #21（発表資料）を PR #22 で閉じます。

ハンズオンでは、素材の [`docs/session12/assets/`](../../docs/session12/assets/) を使います。`templates/` と `app.js` は、この見本の BUG-001 を直す前の形（`data-fragment` に `{{ query }}` がない、イベントを各フォームに付ける素朴な版）です。`test_fragments.py`・`fragments.py` は手順1で、`test_json.py`・`json_api.py` は手順3で、`tests/test_web.py`・`web.py` の末尾に足すテストとルートです。`presentation.md` は手順6で `docs/` にコピーする発表資料の型です。手順どおりに進めると、第12回で変えたファイル（`web.py`・`templates/`・`static/`）と `docs/design/` は見本と一致します。

## 見方

```sh
cd ~/handsoff/examples/todo-app-snapshots
diff -rq session-11 session-12
diff -ru session-11/src/todo/templates session-12/src/todo/templates
diff -u ~/handsoff/docs/session12/assets/app.js session-12/src/todo/static/app.js   # 素朴な版とイベントの委譲
less session-12/docs/bugs/BUG-001.md
less session-12/docs/presentation.md
```

動かして Network タブで見るときや、デモを練習するときは、`workspace/` にコピーしてから起動します（`examples/` の下は変更しない）。

```sh
cp -r ~/handsoff/examples/todo-app-snapshots/session-12 ~/handsoff/workspace/try-12
cd ~/handsoff/workspace/try-12
mise trust && mise install && mise run setup && mise run dev   # http://127.0.0.1:8000
```

| 順 | テスト（`tests/test_web.py`） | 実装 | ハンズオンの手順 |
| --- | --- | --- | --- |
| 1 | `test_一覧の断片はページ全体ではなくulだけ`、`test_断片で追加…`・`test_断片で完了…`（エラーの断片を含む4件）、`test_フォームに断片の送り先がある`、`test_ページがapp_jsを読み込む` | テンプレート、`render_task_list`・`task_list_fragment`・`render_error`・`add_task_fragment`・`mark_done_fragment`、`static/app.js` | 1・2 |
| 2 | `test_JSONで完了に…`・`test_JSONでないタスクを…` | `DoneOut`・`mark_done_json`、`static/done-json.js` | 3 |
| 3 | `test_BUG001_期限切れだけの表示中に完了しても期限切れだけを返す` | `overdue_query`、`data-fragment` の `{{ query }}` | 5 |

- 開発者ツールの Network タブで、「完了」を押したときの `POST /fragments/tasks/{id}/done` のレスポンスが `<ul id="task-list">` の断片だけであることを見る
- JSON 版と比べるときは、`src/todo/templates/base.html` の `app.js` を `done-json.js` に替えて再読み込みする。レスポンスが `{"id": 2, "done": true}` になり、「期限切れだけ」の表示中に完了しても行が消えないことがわかる
- 不具合票は 再現手順 → 期待結果（根拠: 受け入れ条件 (15)・API設計書 A-01）→ 実際の結果 → 原因 → 再発防止 の順。不具合を再現するテスト `test_BUG001_…` を先に書いてから直した
- 発表資料は自分の記録なので、見本を写さず、自分の PR・コミット・不具合票から書く。見本は書き方（4節の構成、作った記録の数字、工夫の根拠の示し方）の参考にする
- 社内プロキシを設定している場合は、`NO_PROXY` に `localhost,127.0.0.1` を入れておく

追いつくときは [examples/README.md](../README.md#遅れた人が追いつく方法) の手順で、フォルダ名を `session-12` にします。
