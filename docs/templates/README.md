# テンプレート

研修で使うひな形です。自分のアプリのリポジトリ（`~/handsoff/workspace/todo-app/`）にコピーして使います。見本は `examples/todo-app-snapshots/` の各回のフォルダにあります。

アジャイルで設計書を少なくする前提です。何を作るかはユーザーストーリー（Issue）と受け入れ条件で決め、細かい振る舞いは TDD のテストで示します（画面設計書とテスト仕様書は作りません）。設計書は「実装者が質問せずに作れるか」を合格基準にします。図は Mermaid で Markdown に書き、Git で差分を追えるようにします。

各ファイルの先頭の `# ` の見出しは、資料の目次に出すためのものです。Issue・PR の本文に使うときは、見出しの行を消してかまいません。

## 要件と設計書

| ファイル | 使う回 | 内容 | 見本 |
| --- | --- | --- | --- |
| [issue_story.md](issue_story.md) | 9 | ユーザーストーリーの Issue（「〜として、〜したい。なぜなら〜」、受け入れ条件、見積の幅と根拠、関連） | `session-09/docs/stories.md`（Issue の控え） |
| [requirements.md](requirements.md) | 9 | 要件メモ（目的・背景、業務フロー図、状態遷移図、非機能要件、制約、対象外、ストーリー一覧へのリンク） | `session-09/docs/requirements.md` |
| [api-design.md](api-design.md) | 10 | API設計書（エンドポイント、リクエスト・レスポンス例、ステータスコード、入力チェックとエラー表示の文言、シーケンス図、設計レビューで出た質問） | `session-10/docs/design/api.md` |
| [db-design.md](db-design.md) | 10 | DB設計書（ER図、テーブル定義、制約、計算で求める値） | `session-10/docs/design/db.md` |
| [architecture.md](architecture.md) | 10 | システム構成図（構成要素、通信経路とポート、ミドルウェアとバージョン、環境変数） | `session-10/docs/design/architecture.md` |

「見本」は `examples/todo-app-snapshots/` の下のパスです。

## Issue と PR

| ファイル | 使う回 | 内容 | 見本 |
| --- | --- | --- | --- |
| [pull_request.md](pull_request.md) | 5 以降 | PR の説明（目的・変更点・確認方法・セルフチェック） | — |
| [issue_task.md](issue_task.md) | 5 以降 | タスクの Issue（目的・やること・完了条件、第9回以降は見積の幅） | — |
| [bug-report.md](bug-report.md) | 12 | 不具合票（再現手順・期待結果・実際の結果） | `session-12/docs/bugs/BUG-001.md` |

GitHub・GitLab では、次の場所に置いたテンプレートが自動で使われます。

| ホスティング | PR のテンプレート | Issue のテンプレート |
| --- | --- | --- |
| GitHub | `.github/pull_request_template.md` | `.github/ISSUE_TEMPLATE/story.md`・`task.md`・`bug.md` |
| GitLab | `.gitlab/merge_request_templates/Default.md` | `.gitlab/issue_templates/story.md`・`task.md`・`bug.md` |
