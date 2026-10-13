# 第8回 見本

[第8回の資料](../../docs/session08/README.md) の成果物「テスト＋CI＋期限順の一覧」の見本は [`todo-app-snapshots/session-08/`](../todo-app-snapshots/session-08/) です。第7回の終わり（[`session-07/`](../todo-app-snapshots/session-07/)）に、テストと CI と「期限が近い順に並べる」（TDD）を足しました。

| ファイル | 内容 |
| --- | --- |
| [commit-log.md](commit-log.md) | ハンズオンの手順どおりに進めたときのコミットの並び（テスト → CI → レッドとグリーン → リファクタ）と、PR の本文の例 |

## 第7回から変わったもの

| 種類 | ファイル | ハンズオン |
| --- | --- | --- |
| 設定 | `pyproject.toml` に pytest・`testpaths`・テストの N802 を外す・mypy の `files` に `tests`、`mise.toml` に `test`（`check` が ruff・mypy・pytest）、`.gitignore` に `.pytest_cache/` | 手順1 |
| テスト（36件） | `tests/test_models.py`（状態と入力チェック。`parametrize`）、`tests/test_store.py`（同じテストを `MemoryStore` と `JsonStore` で。fixture の `params`・`tmp_path`）、`tests/test_cli.py`（`MemoryStore` と固定の「今日」で `main` を動かす。`capsys`）、`tests/test_sort.py`（並べ替え） | 手順2〜4・6・7 |
| CI | `.github/workflows/check.yml`（push と PR ごとに mise を入れて `mise run setup`・`mise run check`） | 手順5 |
| 実装 | `src/todo/models.py` の `sort_by_due`（期限が近い順、期限なしは最後、同じなら id の順）、`src/todo/cli.py` の `run_list` で使う | 手順6・7 |
| 文書 | `README.md`（`mise run test`、CI、`tests/`、テストの規約） | 手順8 |

- 模範の `tests/test_models.py` と `tests/test_sort.py` には、ハンズオンで書かないテスト（`parse_due`、タイトルの100文字、元のリストを変えないこと など）も入っている

## 見方

```sh
cd ~/handsoff/examples/todo-app-snapshots
diff -rq session-07 session-08
diff -u session-07/src/todo/models.py session-08/src/todo/models.py   # TDD で足した sort_by_due
cd session-08
mise trust && mise install && mise run setup
mise run check
```

テストを先に書いた順序はフォルダには残っていません。流れは [commit-log.md](commit-log.md) で読めます。

追いつくときは [examples/README.md](../README.md#遅れた人が追いつく方法) の手順で、フォルダ名を `session-08` にします。
