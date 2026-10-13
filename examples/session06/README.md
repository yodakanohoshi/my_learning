# 第6回 見本

[第6回の資料](../../docs/session06/README.md) の成果物「TODO の CLI＋アプリのリポジトリ」の見本は [`todo-app-snapshots/session-06/`](../todo-app-snapshots/session-06/)（模範の TODO アプリの第6回終了時点）です。ハンズオンの手順7で足す `--due` と `list --overdue` まで入っています。

## `session-06/` に入っているもの

| ファイル | 内容 | ハンズオン |
| --- | --- | --- |
| `.gitignore` | `.venv/`・`__pycache__/`・`tasks.json` を入れない | 手順2でコピー |
| `mise.toml` | Python 3.12 と uv。`mise run setup` | 手順2でコピー（第4回と同じ形） |
| `pyproject.toml`・`uv.lock` | 依存パッケージなし。`[tool.uv] package = false`（パッケージにせず `todo.py` を実行する。第7回で消す） | 手順2でコピー |
| `todo.py` | 1ファイルの CLI。add・list・done、`--due`・`list --overdue`。`tasks.json` に保存 | 手順3〜7で雛形から書く |
| `README.md` | 使い方 | ハンズオンでは作らない（参考） |

## 見方

```sh
cd ~/handsoff/examples/todo-app-snapshots/session-06
less todo.py
```

| 見るところ（`todo.py`） | 扱った書き方 | ハンズオン |
| --- | --- | --- |
| `load_tasks`・`save_tasks` | `with` と例外（`FileNotFoundError` だけを捕まえる）、JSON の読み書き | 手順4 |
| `add_task`・`mark_done` | 型ヒント、`max(..., default=0)` とジェネレータ式、`raise` | 手順5 |
| `parse_due`・`is_overdue`・`format_task` | `date` と文字列の変換、`dict.get`（期限のないタスク）、f-string | 手順7 |
| `list` の処理 | 内包表記で期限切れだけを取り出す | 手順7 |
| `build_parser`・`main` | argparse のサブコマンド、`match` による振り分け、終了コード、`if __name__ == "__main__"` | 手順3・6 |

## 動かし方

`examples/` の下は変更しないでください。試すときは `workspace/` にコピーします。

```sh
cp -r ~/handsoff/examples/todo-app-snapshots/session-06 ~/handsoff/workspace/try-05
cd ~/handsoff/workspace/try-05
mise trust && mise install && mise run setup
python todo.py add "牛乳を買う" --due 2026-11-01
python todo.py list
```

追いつくときは、このフォルダを `workspace/todo-app` にコピーして `git init` します（手順は [examples/README.md](../README.md#遅れた人が追いつく方法)）。
