# TODO アプリ

コマンドラインで使う TODO・タスク管理アプリです。タスクの追加・一覧・完了ができ、期限を付けると期限切れのものだけを表示できます。

## 開発環境

[mise](https://mise.jdx.dev/) と [uv](https://docs.astral.sh/uv/) を使います。システムの Python は使いません。

```sh
mise trust && mise install   # Python 3.12 と uv を入れる
mise run setup               # 仮想環境（.venv）を uv.lock どおりに作る
```

## 使い方

| やること | コマンド |
| --- | --- |
| 追加する | `python todo.py add "牛乳を買う"` |
| 期限付きで追加する | `python todo.py add "レポートを出す" --due 2026-11-01` |
| 一覧を見る | `python todo.py list` |
| 期限切れだけを見る | `python todo.py list --overdue` |
| 完了にする | `python todo.py done 3`（3 は一覧の左端の番号） |
| ヘルプ | `python todo.py --help`、`python todo.py add --help` |

```console
$ python todo.py add "レポートを出す" --due 2026-11-01
追加しました:   1 [未着手] レポートを出す（期限 2026-11-01）
$ python todo.py list
  1 [未着手] レポートを出す（期限 2026-11-01）
$ python todo.py done 1
完了にしました:   1 [完了] レポートを出す（期限 2026-11-01）
```

- タスクはカレントディレクトリの `tasks.json` に保存する（`.gitignore` でリポジトリには入れない）
- 状態は「未着手」「完了」「期限切れ」（完了していない・期限が今日より前）の3つ。完了したものは期限切れにならない
