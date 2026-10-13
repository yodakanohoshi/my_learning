# 第7回 見本

[第7回の資料](../../docs/session07/README.md) の成果物「`src/todo/` パッケージ＋ruff・mypy の設定と README（PR でマージ）」の見本は [`todo-app-snapshots/session-07/`](../todo-app-snapshots/session-07/) です。第6回の `todo.py` を `src/todo/` パッケージに整理しました。ハンズオンの手順1〜6をそのまま進めると、この形になります。

| ファイル | 内容 |
| --- | --- |
| [pr-description.md](pr-description.md) | リファクタリング PR の説明文とセルフレビューの見本 |

## 第6回から変わったもの

| ファイル | 内容 |
| --- | --- |
| `src/todo/cli.py` | 手順1で `todo.py` を `git mv` で移し、手順4で素材に置き換えた。コマンドの解釈と表示。`main(argv, store=, today=)` で保存先と「今日」を差し替えられる |
| `src/todo/models.py` | 手順2。`Task`（`frozen=True` の dataclass）、`Status`（Enum: `TODO`・`DONE`・`OVERDUE`）、入力チェック（`validate_title`・`parse_due`） |
| `src/todo/store.py` | 手順3。保存先の約束 `TaskStore`（Protocol）と、`JsonStore`（`tasks.json`）・`MemoryStore`（メモリ）。継承せずに同じメソッドを持つだけ（ダックタイピング） |
| `pyproject.toml` | 手順1で `package = false` を消し、エントリポイント `todo = "todo.cli:main"` と `uv_build`。手順5で ruff（ルールごとの理由のコメント）と mypy（strict）の設定 |
| `mise.toml` | 手順5。`lint`・`fmt`・`typecheck`・`check` のタスク |
| `.gitignore` | 手順5。`.mypy_cache/`・`.ruff_cache/` を足した |
| `README.md` | 手順6でこの見本をコピーした（第6回のハンズオンでは作っていない）。開発環境・使い方（`uv run todo ...`）・コードの構成・コーディング規約（人が見ること） |

## 見方

```sh
cd ~/handsoff/examples/todo-app-snapshots
diff -rq session-06 session-07                       # 増えた・消えたファイル
diff -u session-06/todo.py session-07/src/todo/cli.py   # 1ファイルからの分け方
cd session-07
mise trust && mise install && mise run setup
mise run check                                       # ruff と mypy が通る
uv run todo list
```

追いつくときは [examples/README.md](../README.md#遅れた人が追いつく方法) の手順で、`session-06` を `session-07` に変えます。
