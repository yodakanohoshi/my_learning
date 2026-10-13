# 研修ハンズオン

1年目エンジニア研修（週1回×全12回。回の構成は docs/curriculum.md が正本）のファイル一式です。
**このディレクトリ自体は git 管理しません。** 研修中に受講者が git 管理するのは、`workspace/` の下の第5回の手順書のリポジトリと TODO アプリのリポジトリだけです（git の使い方は第5回で扱う）。

| ディレクトリ | 内容 | mise |
| --- | --- | --- |
| `docs/` | 資料（全体概要、各回の資料、テンプレート、タグ一覧、未確定事項） | なし |
| `examples/` | 研修中に作るものの見本。見本の TODO アプリ `examples/todo-app/` と、その各回終了時点の `examples/todo-app-snapshots/` を含む | `examples/mise.toml`（`todo-app/` と各スナップショットは独自の mise.toml） |
| `workspace/` | 研修中に作るものの置き場 | `workspace/mise.toml` |
| `tools/` | 研修で動かすスクリプト（タグ一覧の生成、資料の検査） | `tools/mise.toml` |

まず [docs/README.md](docs/README.md)（全体概要）を読んでください。

- 各回のディレクトリは `sessionNN/`（01〜12）です。資料・見本・作業場所で同じ番号を使います
- 全回を個人で進めます。第1〜4回の作業場所は `workspace/sessionNN/`、第5回は `workspace/session05/`（手順書のリポジトリ）、第6回以降は `workspace/todo-app/`（TODO アプリのリポジトリ）です
- 見本の TODO アプリ `examples/todo-app/` は最新（第12回終了時点）で、各回終了時点の状態は `examples/todo-app-snapshots/session-NN/`（06〜12）にあります。どれも git を使わない普通のフォルダで、フォルダ単体で動きます（[examples/README.md](examples/README.md)）
- 受講者に配る一式は `tools/` の `mise run dist -- <出力先>` で作ります（`.git` と講師用の `instructor.md` などを除いてコピーする）

## 環境構築（講師・教材作成者向け）

受講者向けの環境構築手順は第4回の資料にあります。ここでは、このファイル一式を手元で動かす手順だけを書きます。

1. mise をインストールし、シェルで有効にする（[公式の手順](https://mise.jdx.dev/getting-started.html)）

    ```sh
    curl https://mise.run | sh
    echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc
    exec bash
    ```

2. `tools/` の環境を作り、資料を検査する

    ```sh
    cd tools
    mise trust && mise install   # Python 3.12 と uv
    mise run setup               # uv.lock どおりに依存パッケージを入れる
    mise run check               # 資料の冒頭形式とタグを検査
    mise run test                # スクリプトの ruff・mypy・pytest
    ```

3. 見本の TODO アプリを動かす: [examples/README.md](examples/README.md) の手順どおり（`examples/todo-app/` とスナップショットはそれぞれ単体で動く）

4. 受講者に配る一式を作る（研修ディレクトリの外の、空か存在しないディレクトリへ）

    ```sh
    cd ../tools
    mise run dist -- <出力先>
    ```

mise の設定は親ディレクトリから引き継がれるので、回ごとに別のバージョンが必要な場合は、下位のディレクトリに `mise.toml` を置けば上書きできます。初めて入るディレクトリでは `mise trust && mise install` を実行してください。

社内プロキシなど未確定の事項は [docs/open-questions.md](docs/open-questions.md) にまとめています。
