# 第4回 実行環境の整備（講師用）
tag: env-mise, env-python
前提タグ: linux-シェル, linux-アプリ, linux-ネットワーク
所要: 座学15分 / ハンズオン45分

<!-- 講師用。受講者に配るときはこのファイルを除く -->

## 進行メモ

| 時刻 | 内容 | メモ |
| --- | --- | --- |
| 0:00 | 座学: まとめ（15分） | 「システムの Python を使わない理由」（3分）→「3つの層」（4分）→「mise」「uv」の表（5分）→「社内で必要な設定」（3分）。成果物の環境構築手順書（README.md）は手順7で隣の人が使い、第5回でリポジトリにすると予告する |
| 0:15 | ハンズオン 1 システムの Python（4分） | `python3 --version` を隣の人と比べさせる。たまたま 3.12 の人こそ、システムの Python に頼ると後で困ると伝える |
| 0:19 | ハンズオン 2 mise を入れる（7分） | 最初に手順書のテンプレートをコピーさせる。`curl https://mise.run` はネットワーク次第なので、0:26 で入っていない人は講師の画面で続きを見せ、あとで入れてもらう。`.bashrc` のコピーは `.bashrc.bak`（第2回）を上書きしない名前にする |
| 0:26 | ハンズオン 3 mise で固定する（7分） | `--path .` を必ず口頭で強調する（「つまずきやすい点」の1行目）。外に出て比べるステップで、`cd` だけで版が変わることを全員に見せる |
| 0:33 | ハンズオン 4 uv（8分） | `uv init` のオプションの付け忘れが多い。`.venv/bin/python` がリンクになっているのを見せ、「.venv は渡さない」の伏線にする |
| 0:41 | ハンズオン 5 mise.toml の env と tasks（8分） | ヒアドキュメントの `EOF` までをまとめて貼らせる。`mise run setup` がわざと失敗するステップは、エラーの1行目を読ませてから `uv lock` に進む |
| 0:49 | ハンズオン 6 渡すものと再現（5分） | `is not trusted` の表示を全員に見せる。`mise run` は自動で信頼するので、受け取った `mise.toml` は先に `cat` で見ることを押さえる |
| 0:54 | ハンズオン 7 隣の人の手順書で再現（6分） | 席を替わり、相手の PC で相手の README だけを見て打つ。手順書に書いていないことは、講師も作った本人も口で教えない。指摘は「うまくいかないとき」に書かせる。終わらなかった分は第5回の Issue の題材にしてよい |

時間が押したら、手順1の `apt-cache rdepends` と手順4の `.venv` の中を見るステップを講師の画面だけにします。手順3（`--path .` と `cd` での切り替え）と手順5（`--locked` で止まって直す）は削らないでください。手順7が3分を切りそうなら、自分で `~/session04-try` を作って README どおりに打つだけにし、指摘のやり取りは第5回までに各自で済ませてもらいます（第5回は冒頭から自分の一式をリポジトリにするので、時間を取れない）。

第4回は振り返り・宿題・発展課題を設けません。元の宿題だった `mise.toml` と環境構築手順書（README）は、手順2からハンズオンの中で書きます。第5回はこのディレクトリのファイル（`README.md`・`mise.toml`・`pyproject.toml`・`uv.lock`・`main.py`）をコピーしてリポジトリにします。

### 事前に確認すること

- 社内ネットワークから次の宛先に届くか（[open-questions.md](../open-questions.md) の Q1・Q5）。届かないと手順2〜5が止まるので、研修前に受講者と同じ条件の PC で通しで試す
    - `mise.run`（mise のインストール）、`github.com` と `objects.githubusercontent.com`（mise が Python と uv を取得）、`pypi.org` と `files.pythonhosted.org`（uv がパッケージを取得）
- 社内 CA 証明書が要る環境で、mise・uv が証明書エラーにならないか（Q3）。uv は既定では OS の証明書ストアを読まないので、`UV_NATIVE_TLS=1`（または `--native-tls`）が要る。mise がエラーになる場合の対処は、講師の PC で確かめてから受講者に伝える
- 受講者の Ubuntu の版（Q10）。Ubuntu 24.04 ならシステムの Python も 3.12 で、手順1の「版が違う」が見えにくい。その場合は講師の画面（26.04 なら 3.14）と比べる
- 受講者が第2回の環境設定手順書を仕上げているか。手順7で「確認」の行を使う
- `workspace/mise.toml`（`[tools]` に `python = "3.12"` だけ）が配られていること。手順3で `mise config ls` に出る

### この回の検証について

資料のコマンドは、Ubuntu 26.04（bash 5.3）で mise 2026.10.7、uv 0.9.30、Python 3.12.15 を使って確かめました。`mise use` が `--path .` なしで親の `mise.toml` に書くこと、`uv add rich` で入る5パッケージ（hello-todo を含む）、`--locked` のエラー文、コピーした先での `is not trusted` の警告、`mise activate bash` が `cd` を関数にすることは実際の出力です。mise は `mise run`・`mise install`・`mise exec` を実行したとき、その設定を自動で信頼します（mise 2026.10 の `mise trust --help`）。信頼の警告が出るのは、activate したシェルで `cd` したときです。

## つまずきやすい点

| 症状 | 原因 | 対処 |
| --- | --- | --- |
| `mise use` したのに `session04/mise.toml` ができず、`workspace/mise.toml` が書き換わる | `mise use` は「いちばん近い `mise.toml`」に書き込む。`workspace/` に研修用の `mise.toml` がある | `mise use --path . ...` でやり直し、`workspace/mise.toml` を元に戻す（`[tools]` の `python = "3.12"` だけ） |
| `uv init` のあと `.git` ができている | `--vcs none` を付け忘れた | `rm -rf .git`。Git は第5回で自分で `git init` する |
| `.python-version` ができている | `--no-pin-python` を付け忘れた | 消してよい。Python の版は `mise.toml` だけで決める（2か所にあると食い違う） |
| `uv init` で `README.md` が上書きされた・されない | `uv init` は既にある `README.md` を上書きしない | 手順2でテンプレートをコピーしていれば残る。順番を逆にした人は、`uv init` の後にテンプレートをコピーし直す |
| `which python` が `/usr/bin/python` を指す・`command not found` | `.bashrc` に activate を書いていない、または `exec bash` していない | `tail -1 ~/.bashrc` と `type -t mise` を確かめる |
| `mise: command not found`（`exec bash` の後） | `curl https://mise.run \| sh` が途中で止まった | `ls ~/.local/bin/mise`。なければプロキシを確かめて入れ直す |
| `curl https://mise.run` が止まる、`mise use` がタイムアウトする | プロキシの環境変数がない、または小文字版がない | `env \| grep -i _proxy`。第2回の手順書の 3-1 |
| `uv add` が `invalid peer certificate: UnknownIssuer` | 社内 CA を uv が読んでいない | `export UV_NATIVE_TLS=1` を `.bashrc` に書いて `exec bash` |
| `mise run hello` で `ModuleNotFoundError: No module named 'rich'` | 別のディレクトリで実行した、または `mise run setup` をしていない | `pwd` と `mise run setup` |
| 手順5で `[env]` を足しても `which python` が `.venv` を指さない | プロンプトがまだ戻っていない、または `.venv` がない | Enter をもう一度押す。`mise run setup` で `.venv` を作る |
| ヒアドキュメントの後、プロンプトが `>` のまま | `EOF` の行まで貼っていない | `EOF` と打って Enter。`cat mise.toml` で重複を確かめ、重複していたら `nano` で消す |
| `mise run setup` が `The lockfile at uv.lock needs to be updated` | `pyproject.toml` を変えたのに `uv lock` していない（手順5ではわざと起こす） | `uv lock` してから `mise run setup` |
| 手順6・7で `is not trusted` が出ない | 同じパスを前に信頼した、または `mise run` を先に打った | 手順7は手順6と違う名前（`~/session04-try`）にする。出なくても先に進んでよい |
| `uv` が意図しない Python（3.13 以降のシステムの Python）で `.venv` を作ろうとする | mise を有効にしていないシェルで `uv` を直接実行した | `requires-python` に上限（`<3.13`）があり、`UV_PYTHON_DOWNLOADS=never` なので、エラーで止まって気づける |

## 解答例

### 手順ごとの表示

| 手順 | コマンド | 表示（検証環境） |
| --- | --- | --- |
| 1 | `python3 --version` | `Python 3.14.4`（Ubuntu 26.04。24.04 なら 3.12 系） |
| 1 | `dpkg -S /usr/bin/python3` | `python3-minimal: /usr/bin/python3` |
| 1 | `head -5 /usr/lib/python3*/EXTERNALLY-MANAGED` | `[externally-managed]`、`Error=To install Python packages system-wide, try apt install ...` |
| 2 | `type -t mise cd` | `function` が2行 |
| 3 | `cat mise.toml` | `[tools]`、`python = "3.12"`、`uv = "0.9"` |
| 3 | `mise ls --current` | `python 3.12.15 ~/handsoff/workspace/session04/mise.toml 3.12` と uv の行 |
| 3 | `cd ~` の後の `type uv` | `bash: type: uv: not found` |
| 4 | `uv add rich` | `+ markdown-it-py==4.2.0`、`+ mdurl==0.1.2`、`+ pygments==2.21.0`、`+ rich==15.0.0` |
| 4 | `ls -l .venv/bin/python` | `python -> ~/.local/share/mise/installs/python/3.12/bin/python3` |
| 5 | `mise tasks` | `hello タスク一覧を表示する`、`setup 依存パッケージを uv.lock どおりに入れる` |
| 5 | 上限を付けた後の `mise run setup` | ``The lockfile at `uv.lock` needs to be updated, but `--locked` was provided. To update the lockfile, run `uv lock`.`` と `[setup] ERROR task failed` |
| 6 | コピー先に `cd` | ``mise WARN ~/session04-check/mise.toml is not trusted, run `mise trust` to enable it`` |
| 6 | `du -sh .venv` | 約 8MB |

最終形の `mise.toml`・`pyproject.toml` は [examples/session04/](../../examples/session04/README.md) と同じです（見本の `pyproject.toml` の `description` だけ違う）。

### 環境構築手順書（README.md）

- 見本: [examples/session04/README.md](../../examples/session04/README.md)。手順7の後に見せる（先に見せると写すだけになる）
- テンプレートは `docs/session04/assets/環境構築手順書.md`。1行目の `# 環境構築手順` は、第5回のコンフリクトの演習で書き換えるので変えさせない
- 手順書で見るのは次の点
    - 手順ごとに「確認」があり、期待する表示（`mise ls --current` の行、最後の行の `.venv/bin/python`）で書かれている
    - `cd` する場所、`mise trust` の前に中身を見ることが書かれている
    - 渡すファイルに `.venv/` が入っていない
    - 「うまくいかないとき」に、手順7で隣の人が実際に止まった所が入っている
    - 「元に戻す方法」が `.bashrc.before-mise` を使っている
- 手順7で指摘が出やすいのは「どのディレクトリで実行するか」「`mise trust` の前に何を見るか」「成功したかどうかの判断方法」の3点

### 講師が見せる補足（任意）

時間が余ったときに講師の画面で見せます。受講者の課題にはしません。

```sh
# Node.js も mise で管理する（nodejs.org に届く必要がある）
mise use --path . node@22
cat mise.toml          # [tools] に node = "22" が増える
cd ~ && type node; cd -  # ディレクトリの外では見つからない（またはシステムの node）

# 開発のときだけ使うパッケージ
uv add --dev ruff      # pyproject.toml に [dependency-groups] の dev が増える（第7回で使う）

# uv.lock を作り直すと、いつ作ったかで版が変わりうる
cp uv.lock /tmp/uv.lock.old; rm uv.lock; uv lock; diff /tmp/uv.lock.old uv.lock
```

- `dependencies` は動かすのに必要なもの、`dev` は開発するときだけ必要なもの。第7回の ruff、第8回の mypy・pytest は `dev` に入る
- `uv.lock` を作り直したときに差分が出るのは、`pyproject.toml` の範囲内で新しい版が出ていた場合。そのため `uv.lock` も渡し、リポジトリに入れる

## 評価の観点

- 隣の人が README だけで `mise run hello` まで進めたか（横断テーマ「環境の再現性」の完了条件）。止まった所を README に反映したか
- `mise.toml` がプロジェクトのディレクトリにあり、親の `workspace/mise.toml` に頼っていないか（`mise config ls`）
- `.venv` を渡さない理由を「作り直せる」「PC ごとのパスを含む」の2点で説明できるか

## カリキュラムとの関係（報告事項）

- 2026-10-13 の見直しで、所要を座学15分 / ハンズオン45分にし、振り返り・宿題・発展課題をなくした。宿題だった `mise.toml` と環境構築手順書（README）は手順2からハンズオンの中で書き、元の宿題の「別の場所にコピーして再現」は手順6に入れた
- 元の演習「隣の人の手順書だけを見て環境を構築」は、第2回の環境設定手順書を交換する形だった。第2回の設定は全員が済ませているので、今回は第4回の README を交換して再現し、第2回の手順書は前提を確かめる「確認」の行だけを使う形にした
- Node.js（元の発展課題）、`uv add --dev`、`uv.lock` の作り直しは「講師が見せる補足（任意）」に移した
- 研修のディレクトリ構成では `workspace/` に `mise.toml` があるため、`mise use` が親に書き込むというつまずきが生まれる。`--path .` で対処し、手順3で親の `mise.toml` との関係を図で見せる
