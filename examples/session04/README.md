# 環境構築手順

WSL の Ubuntu に mise と uv を入れ、`mise run hello` が動くところまでの手順です。

> [第4回の資料](../../docs/session04/README.md) のハンズオンで書く環境構築手順書（テンプレートは [docs/session04/assets/環境構築手順書.md](../../docs/session04/assets/環境構築手順書.md)）の見本です。
> このディレクトリ自体が見本のプロジェクト（タスク一覧を表で出す `hello-todo`）で、下の手順どおりに動きます。

- 対象: WSL の Ubuntu 26.04（24.04 でも同じ手順）
- 所要時間: 約15分（mise と Python のダウンロードを含む）
- 前提: 第2回の環境設定手順書（PATH・プロキシ）が済んでいること。社内ネットワークでは `mise.run`・`github.com`・`pypi.org` にプロキシ経由で届くこと

動作を確かめた版: mise 2026.10.7、Python 3.12.15、uv 0.9.30（Python と uv は mise が入れる）

## 1. mise を入れる（PC ごとに1回だけ）

```sh
curl https://mise.run | sh
cp ~/.bashrc ~/.bashrc.before-mise
echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc
exec bash
mise --version
```

確認: `2026.10.7 linux-x64 (...)` のように版が出る（数字は入れた時期で変わる）。`type -t mise` が `function`

## 2. Python と uv を入れる

```sh
cd ~/handsoff/examples/session04   # 受け取ったファイルのあるディレクトリ
cat mise.toml                      # 中身を見てから信頼する
mise trust
mise install
mise ls --current
```

確認: python と uv の行が、このディレクトリの `mise.toml` を指している

```console
python  3.12.15  ~/handsoff/examples/session04/mise.toml  3.12
uv      0.9.30   ~/handsoff/examples/session04/mise.toml  0.9
```

## 3. 依存パッケージを入れる

```sh
mise run setup   # 中身は uv sync --locked
```

確認: `+ rich==15.0.0` などが出て、`.venv/` ができる。`The lockfile at uv.lock needs to be updated` と出たら、渡した人が `uv lock` を忘れている

## 4. 動かす

```sh
mise run hello
```

確認: タスクの表が出て、最後の行が `.venv/bin/python` を指している

```console
                  タスク一覧
┏━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┓
┃ ID ┃ タイトル         ┃ 期限       ┃ 状態   ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━┩
│ 1  │ 牛乳を買う       │ 2026-11-01 │ 未着手 │
│ 2  │ 研修の資料を読む │ 2026-10-19 │ 完了   │
│ 3  │ 歯医者を予約する │ -          │ 未着手 │
└────┴──────────────────┴────────────┴────────┘
Python 3.12.15 (~/handsoff/examples/session04/.venv/bin/python)
```

## 渡すファイルと渡さないファイル

| ファイル | 役割 | 渡すか |
| --- | --- | --- |
| `mise.toml` | Python・uv の版、環境変数、タスク（`setup`・`hello`） | 渡す |
| `pyproject.toml` | プロジェクトの情報と、直接使うパッケージ（`rich>=15.0.0`） | 渡す |
| `uv.lock` | 間接的に使うものも含めた、全パッケージの正確な版 | 渡す |
| `main.py` | 動作確認用のプログラム | 渡す |
| `.venv/` | 仮想環境。`mise run setup` でいつでも作り直せる。中のリンクは作った PC のパスを指す | **渡さない**（`.gitignore` に書く） |

## うまくいかないとき

| 症状（表示） | 原因 | 対処 |
| --- | --- | --- |
| `curl https://mise.run` や `mise install` が止まる、`Could not resolve host`（6）・timed out（28） | プロキシの環境変数がない | `env \| grep -i _proxy`。第2回の環境設定手順書の 3-1 |
| `SSL certificate problem`（60）、uv だけ `invalid peer certificate` | 社内 CA 証明書が登録されていない／uv が OS の証明書を読んでいない | 第2回の手順書の 3-3。uv は `export UV_NATIVE_TLS=1` を `~/.bashrc` に書く |
| `mise: command not found` | `.bashrc` を読み直していない | `exec bash` かターミナルを開き直す |
| ``mise.toml is not trusted`` | コピー・受け取った設定は、信頼するまで `[env]` が読まれない | `cat mise.toml` で中身を見てから `mise trust` |
| `ModuleNotFoundError: No module named 'rich'` | `mise run setup` をしていない | `mise run setup` |
| `which python` が `.venv` を指さない | `mise.toml` のあるディレクトリの外にいる、または activate が効いていない | `pwd` と `tail -1 ~/.bashrc` を確かめる |

## 元に戻す方法

```sh
cp ~/.bashrc.before-mise ~/.bashrc   # activate の行を消す
exec bash
rm -rf .venv                         # このプロジェクトの仮想環境だけ消す
```

確認: 新しいターミナルで `type -t mise` が `function` でなくなる（`file` か、何も出ない）。mise 自体も消すときは、戻す前に `mise implode`（mise と入れた Python・uv を消す）
