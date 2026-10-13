# 見本

研修中に作るものの見本です。受講者の作業場所は、第1〜5回が `workspace/sessionNN/`、第6回以降が `workspace/todo-app/`（自分の TODO アプリのリポジトリ）です。

| ディレクトリ | 内容 |
| --- | --- |
| `session01/` 〜 `session05/` | 個人演習の成果物の見本（作業ログ、手順書、観察した結果の例、mise.toml＋README、個人リポジトリ） |
| `session06/` 〜 `session12/` | その回の見本の案内。中身は `todo-app-snapshots/` の各回終了時点のフォルダ |
| `todo-app/` | 模範の TODO アプリの最新（第12回終了時点。`todo-app-snapshots/session-12/` と同じ） |
| `todo-app-snapshots/` | 模範の TODO アプリの各回終了時点の状態（下の表） |

## 模範の TODO アプリ

各回終了時点の状態を `todo-app-snapshots/` の下にフォルダで置いています。どのフォルダも単体で動きます（git は使っていません）。前の回のフォルダに、その回の分を足したものです。

| フォルダ（`todo-app-snapshots/` の下） | 終わっていること |
| --- | --- |
| [`session-06/`](todo-app-snapshots/session-06/) | 1ファイルの CLI `todo.py`（add・list・done、`tasks.json` に保存、`--due` と `list --overdue`） |
| [`session-07/`](todo-app-snapshots/session-07/) | `src/todo/` パッケージへの整理（dataclass・Enum・Protocol）、ruff・mypy の設定、`uv run todo`、README（開発環境・使い方・コーディング規約） |
| [`session-08/`](todo-app-snapshots/session-08/) | pytest のテスト、期限が近い順の並べ替えと一覧の表示（TDD）、CI（`.github/workflows/check.yml`）、README（テストと CI） |
| [`session-09/`](todo-app-snapshots/session-09/) | 要件メモ（業務フロー図・状態遷移図・非機能要件・対象外）、ユーザーストーリー S-01〜S-04（Issue #8〜#11 の控え、受け入れ条件 (1)〜(15)） |
| [`session-10/`](todo-app-snapshots/session-10/) | API・DB設計書（設計レビューで出た質問の反映つき）、システム構成図 |
| [`session-11/`](todo-app-snapshots/session-11/) | Web 版（FastAPI＋Jinja2＋SQLite、素の HTML フォーム）、`TaskStore` の SQLite 版 `SqliteStore`、受け入れ条件 (1)〜(15) のテスト（`tests/test_web.py`）、README（Web 版の使い方） |
| [`session-12/`](todo-app-snapshots/session-12/) | fetch による部分更新（HTML 断片を返す URL と `app.js`）、比較用の JSON 版（`done-json.js`）、API設計書・システム構成図 1.1、不具合票 BUG-001 とその修正（再現テストつき）、発表資料（4節: 何を作ったか → 構成 → デモ手順 → 工夫1つ） |

回ごとに増えたものは、前の回のフォルダとの差分で見られます。テストを先に書いた（レッド → グリーン → リファクタ）順序はフォルダには残っていないので、テストとコードを並べて読んでください。

```sh
cd ~/handsoff/examples/todo-app-snapshots
diff -rq session-10 session-11   # 第11回で増えた・変わったファイル
diff -ru session-10 session-11   # 中身の差分
```

## mise のタスク（このディレクトリで実行）

```sh
cd ~/handsoff/examples
mise trust && mise install
mise run app-setup     # 模範の TODO アプリの Python と依存パッケージを入れる（初回だけ）
mise run app           # 模範の TODO アプリ（最新）を起動する → http://127.0.0.1:8000
mise run app-check     # 模範の TODO アプリのリント・型チェック・テスト
```

## 遅れた人が追いつく方法

追いつきたい回のフォルダを `workspace/todo-app` にコピーし、`git init` して最初のコミットを作ります。`examples/` の下は変更しないでください。下の例は、第11回の終わりの状態から始める場合です。

```sh
cd ~/handsoff/workspace
mv todo-app todo-app-old   # 自分のリポジトリがあれば、消さずに名前を変えて残す
cp -r ~/handsoff/examples/todo-app-snapshots/session-11 todo-app
cd todo-app
git init -b main
git add . && git commit -m "見本の第11回終了時点から始める"
mise trust && mise install && mise run setup
mise run check   # 第7回以降（第6回は python todo.py --help で確かめる）
```

- GitHub のリポジトリに push するときは、`git remote add origin <URL>` してから `git push -u origin main`（前のリポジトリを使い続けるなら、別名の新しいリポジトリを作る）
- 自分のリポジトリを残して必要なところだけ取り込みたいときは、ブランチを作り、見本を見ながら書いて PR にする（見本で丸ごと上書きしない）

---

## 作成者・講師向け

| タスク・ファイル | 内容 |
| --- | --- |
| `mise run check-all` | 全スナップショット（`todo-app-snapshots/session-*`）と `todo-app/` で、依存を入れてリント・型チェック・テストを順に実行する。第6回は ruff・mypy・pytest がないので、`python todo.py --help` が動くことだけ確かめる |
| `tools/` の `mise run dist -- <出力先>` | 配布物を作る。`.venv`・キャッシュ・`instructor.md` などは含めない |

- 見本を直すときは、その回のフォルダと、それより後の回のフォルダと `todo-app/` に同じ変更を入れる（後の回は前の回に足したもの）。直したら `mise run check-all` で確かめる
- 依存パッケージを変えたら、そのフォルダで `mise exec -- uv lock` を実行して `uv.lock` を作り直す
- `check-all` は各フォルダに `.venv` を作る。配布物には入らないが、要らなければ消す（`rm -rf todo-app-snapshots/*/.venv todo-app/.venv`）
