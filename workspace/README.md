# 作業場所

研修中に作るものを置く場所です。第1〜5回は資料と同じ番号のディレクトリ（`sessionNN/`）、第6回以降はアプリのリポジトリ（`todo-app/`）で作業します。

| ディレクトリ | 使う回 | 中身 | Git |
| --- | --- | --- | --- |
| `session01/` 〜 `session04/` | 第1〜4回 | 個人の作業（作業ログ、環境設定手順書、第3回の Cookie のファイル、mise.toml＋README） | 管理しない |
| `session05/` | 第5回 | 手順書のリポジトリ（第4回の手順書をコピーして作る） | 第5回で `git init` し、`<Gitホスティング>` に push |
| `todo-app/` | 第6〜12回 | TODO アプリのリポジトリ（コードと設計書） | 第6回で自分で作り、`git init` する |

- `todo-app/` は第6回に自分で作るので、最初はありません
- Git で管理するのは `session05/` と `todo-app/` の中だけです。`~/handsoff` と `workspace/` 自体では `git init` しないでください
- `<Gitホスティング>` は未確定です（[open-questions.md](../docs/open-questions.md) の Q4）
- 見本は `examples/sessionNN/` と `examples/todo-app-snapshots/session-NN/`（各回終了時点のアプリ）にあります

## 遅れたとき（第7回以降）

追いつきたい回の前の回のスナップショットを `todo-app/` としてコピーし、`git init` して最初のコミットを作ります。`examples/` の下は変更しないでください。例は第8回を第7回の終わりの状態から始める場合です。

```sh
cd ~/handsoff/workspace
mv todo-app todo-app.old            # 自分の todo-app/ があれば残しておく
cp -r ~/handsoff/examples/todo-app-snapshots/session-07 todo-app
cd todo-app
git init -b main
git add . && git commit -m "見本の第7回終了時点から始める"
git remote add origin <リポジトリのURL>   # 自分のリモートに push する場合
```

- 自分の `todo-app.old/` の変更で残したいものは、ブランチを作って持ってきて、PR で取り込みます
- コピーした後の動かし方は、そのスナップショットの `README.md` に従います

## mise.toml

このディレクトリの `mise.toml`（Python 3.12）は `examples/mise.toml` とバージョンをそろえています。各リポジトリの外にあるので、リポジトリには入りません。リポジトリの中で使う `mise.toml` は、自分で書きます（第4回で手順書用、第6〜7回でアプリ用）。
