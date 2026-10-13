# 第4回 作業場所

[第4回の資料](../../docs/session04/README.md) のハンズオンで、ここに小さな Python プロジェクトと環境構築手順書を作ります。見本は [examples/session04/](../../examples/session04/README.md) です。

ハンズオンが終わると、このディレクトリには次のファイルがそろいます。第5回でこのディレクトリのファイルをリポジトリにします。

| ファイル | 作り方（ハンズオンの手順） | 他人に渡すか |
| --- | --- | --- |
| `README.md` | 手順2でテンプレートをコピーして、このファイルを上書きする。手順ごとに書き足す | 渡す |
| `mise.toml` | 手順3の `mise use --path . python@3.12 uv@0.9`、手順5で `[env]` と `[tasks]` を足す | 渡す |
| `pyproject.toml`・`uv.lock` | 手順4の `uv init ...` と `uv add rich`、手順5で上限を付けて `uv lock` | 渡す |
| `main.py` | 手順4で見本からコピーする | 渡す |
| `.venv/` | `uv add` や `mise run setup` で自動でできる | 渡さない |

- `mise use` には必ず `--path .` を付けてください。付けないと、1つ上の `workspace/mise.toml` が書き換わります
- `uv init` には `--vcs none` を付けてください。Git リポジトリは第5回で自分で作ります
