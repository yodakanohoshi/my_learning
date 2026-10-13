# TODO アプリ

TODO・タスク管理アプリです。タスクの追加・一覧・完了ができ、期限を付けると期限切れのものだけを表示できます。ブラウザから使う Web 版と、コマンドラインから使う CLI があります。

## ドキュメント

| ファイル | 内容 |
| --- | --- |
| [docs/requirements.md](docs/requirements.md) | 要件メモ（Web 版の目的・業務フロー図・状態遷移図・非機能要件・制約・対象外） |
| [docs/stories.md](docs/stories.md) | ユーザーストーリーと受け入れ条件（Issue の控え） |
| [docs/design/api.md](docs/design/api.md) | API設計書（エンドポイント・入力チェックとエラーの文言・シーケンス図） |
| [docs/design/db.md](docs/design/db.md) | DB設計書（ER図・テーブル定義） |
| [docs/design/architecture.md](docs/design/architecture.md) | システム構成図（構成要素・通信経路とポート・設定） |
| [docs/bugs/](docs/bugs/) | 不具合票（BUG-001 など） |
| [docs/presentation.md](docs/presentation.md) | 成果発表の資料（構成図・デモ手順・設計とテストの工夫） |

## 開発環境

[mise](https://mise.jdx.dev/) と [uv](https://docs.astral.sh/uv/) を使います。システムの Python は使いません。

```sh
mise trust && mise install   # Python 3.12 と uv を入れる
mise run setup               # 依存パッケージを uv.lock どおりに入れる
mise run check               # リント・型チェック・テスト（PR を出す前に必ず通す）
```

push と PR のたびに、GitHub Actions（[.github/workflows/check.yml](.github/workflows/check.yml)）が同じ `mise run setup` と `mise run check` を実行する。PR は CI が通ってからマージする。

| タスク | 内容 |
| --- | --- |
| `mise run setup` | 依存パッケージを入れる |
| `mise run dev` | Web 版の開発用サーバを起動する（<http://127.0.0.1:8000>） |
| `mise run db-reset` | Web 版の開発用 DB（`var/todo.db`）を消す |
| `mise run test` | 自動テスト（pytest） |
| `mise run lint` | リントとフォーマットの確認（ruff） |
| `mise run fmt` | フォーマットと、自動で直せるリントの修正 |
| `mise run typecheck` | 型チェック（mypy、strict） |
| `mise run check` | lint・typecheck・test をまとめて実行する |

## 使い方（Web 版）

```sh
mise run dev   # 起動する。止めるときは Ctrl+C
```

ブラウザで <http://127.0.0.1:8000> を開く。社内プロキシを設定している場合は、`NO_PROXY` に `localhost,127.0.0.1` を入れておく。

- 上のフォームでタイトルと期限（任意）を入れて「追加」。追加と完了は、ページ全体を読み直さずに一覧だけを差し替える（`static/app.js`）
- 一覧は期限が近い順。各タスクの「完了」で完了にする
- 「期限切れだけ」で期限切れのタスクだけを表示する（`/?overdue=1`）
- 比較用に、完了だけを JSON の API で行う版（`static/done-json.js`）がある。試すときは `templates/base.html` の `app.js` を `done-json.js` に替える
- データは `var/todo.db`（SQLite）に保存する。場所は環境変数 `TODO_DB_PATH` で変えられる（`mise.toml` で設定）

## 使い方（CLI）

| やること | コマンド |
| --- | --- |
| 追加する | `uv run todo add "牛乳を買う"` |
| 期限付きで追加する | `uv run todo add "レポートを出す" --due 2026-11-01` |
| 一覧を見る（期限が近い順、期限なしは最後） | `uv run todo list` |
| 期限切れだけを見る | `uv run todo list --overdue` |
| 完了にする | `uv run todo done 3`（3 は一覧の左端の番号） |

- タスクはカレントディレクトリの `tasks.json` に保存する（第6回の `todo.py` と同じ形なので、そのまま読める）
- 状態は「未着手」「完了」「期限切れ」（完了していない・期限が今日より前）の3つ。完了したものは期限切れにならない

## コードの構成

| ファイル | 内容 |
| --- | --- |
| `src/todo/models.py` | タスク（`Task`、frozen な dataclass）、状態（`Status`）、入力のチェック、期限順の並べ替え（`sort_by_due`） |
| `src/todo/store.py` | 保存先の約束（`TaskStore`、Protocol）と、その実装 `JsonStore`（tasks.json）・`MemoryStore`（メモリ） |
| `src/todo/cli.py` | コマンドの解釈と表示。保存先は `TaskStore` として受け取る |
| `src/todo/sqlite_store.py` | SQLite の保存先 `SqliteStore`（`TaskStore` の約束を満たす） |
| `src/todo/web.py` | Web 版の URL と画面（FastAPI）。保存先と「今日」は依存関係（`get_store`・`get_today`）で受け取る |
| `src/todo/templates/` | 画面の HTML（Jinja2）。`_` で始まるものは断片（一覧 `_task_list.html`、エラー `_error.html`） |
| `src/todo/static/` | CSS と JavaScript（`app.js`: fetch で HTML 断片を受け取って差し替える、`done-json.js`: 比較用の JSON 版） |
| `tests/` | pytest のテスト。保存先は `MemoryStore` や `tmp_path` の JSON・DB に、「今日」は固定の日付に差し替える |

## コーディング規約

自動で確かめられるものは `pyproject.toml` の ruff と mypy の設定に書いた。人が見ることだけをここに書く。

| 項目 | 決まり |
| --- | --- |
| 型 | すべての関数に型ヒントを書く（mypy の strict で確かめる） |
| 名前 | 関数は動詞（`validate_title`）、真偽値は `is_`・`has_` か形容詞、略さない |
| 関数 | 1つの関数は1つのことだけをする。入力の解釈・処理・表示を分ける |
| 分岐 | 例外的な場合は早期 return で先に抜け、ネストを深くしない |
| コメント | コードを読めばわかることは書かない。「なぜ」を書く |
| データ | 作った後に変えないものは `frozen=True` の dataclass にする |
| テスト | 機能を足すときはテストを先に書く。テストのコミットと実装のコミットを分ける。テスト名には確かめたいことを日本語で書く |
