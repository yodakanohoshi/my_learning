# 未確定事項

社内での確認が終わっていない事項の一覧です。資料では値を推測で埋めず、下の「プレースホルダー」の形で書いています。決まったら、この表の「決定内容」を埋め、プレースホルダーを置き換えてください。

置き換え漏れは次のコマンドで探せます（研修ディレクトリのルートで実行）。

```sh
grep -rn --include='*.md' --include='*.toml' --include='*.py' -e '<社内' -e '<プロキシ' -e '<Git' -e '<リポジトリ' -e '<研修' docs examples workspace tools | grep -v open-questions.md
```

| ID | 事項 | プレースホルダー | 影響する回 | 決定内容 |
| --- | --- | --- | --- | --- |
| Q1 | 社内プロキシのアドレスと認証の有無 | `<社内プロキシのアドレス>`（`http://<ホスト>:<ポート>` の形を想定）、`<社内プロキシのホスト:ポート>`（認証ありの場合に `ユーザー名:パスワード@` を挟むため）、`<プロキシ認証の有無>` | 2〜4 | |
| Q2 | 受講者 PC で WSL を有効化できるか（管理者権限・情報システム部門の許可） | — | 1〜4（全回の前提） | |
| Q3 | 社内 CA 証明書の入手方法 | `<社内CA証明書の入手方法>`、`<社内CA証明書のファイル名>` | 2〜4 | |
| Q4 | Git ホスティング（GitHub か GitLab か）、アカウントの発行方法、認証方式 | `<Gitホスティング>`、`<リポジトリのURL>` | 5〜12 | |
| Q5 | mise・uv・PyPI へプロキシ越しにアクセスできるか | — | 4 以降 | |
| Q6 | 受講者の人数（グループ分けは不要。2026-10-12 に全回を個人で進めることにした） | — | 12（発表の持ち時間） | |
| Q7 | 週2回（全24回）に拡張するか | — | — | 拡張しない。2026-10-12 の見直しで拡張案をなくした（週1回×全12回）。拡張案のテーマの教材は作らない |
| Q8 | 研修ディレクトリ一式の配布方法と、受講者 PC での置き場所 | `<研修ディレクトリの配布方法>`。置き場所は資料上 `~/handsoff` としている | 1 以降 | |
| Q9 | （不要になった）模範リポジトリのコミット作者名 | — | — | 2026-10-12 に見本のアプリ（`examples/todo-app/`）を git を使わないフォルダにしたので不要 |
| Q10 | 受講者 PC の Ubuntu のバージョンと、WSL が Windows のプロキシ設定を引き継ぐか | — | 2〜4 | |
| Q11 | GitHub Actions（GitLab なら Runner）が受講者のリポジトリで使えるか | — | 8 以降 | |
| Q12 | 受講者 PC（WSL）で Docker が使えるか（Docker Desktop のライセンス、または WSL 内の Docker Engine の導入可否） | — | 1 | |

## 補足

### Q1・Q3 社内プロキシと CA 証明書

- 認証付きのプロキシの場合、`HTTP_PROXY` に ID とパスワードを書くことになる。第2回で「秘密情報をファイルや履歴に残さない」扱い（`read -s` で入力するなど）を教えている
- 第3回では、Windows のブラウザから WSL のデモのサーバ（`127.0.0.1:8000`・`localhost:8001`）を開くので、Windows のプロキシ設定の例外に `127.0.0.1;localhost` が要る
- 社内 CA 証明書の配布形式（PEM か DER か）によって、Ubuntu への登録手順（`update-ca-certificates`）が変わる
- uv は既定では OS の証明書ストアを使わない。社内 CA を読ませるには `UV_NATIVE_TLS=1`（または `SSL_CERT_FILE`）が要る（第2・4回の資料に記載）

### Q4 Git ホスティング

- 決まるまで、PR・Issue・ブランチ保護の説明はどちらでも読める書き方にし、固有の操作は「GitHub の場合」「GitLab の場合」に分けて書く
- 用語の違い: Pull Request（GitHub）／Merge Request（GitLab）。資料では「PR」と書き、初出で両方を併記する
- カリキュラムには「GitHub の Issue ラベル」とあるが、GitLab でもラベル機能で同じ運用ができる
- 認証方式（HTTPS とトークンか、SSH 鍵か）とトークンの保存方法を決める必要がある。`git config credential.helper store` はトークンを平文で保存するため、社内規定の確認が要る
- 受講者に自分のリポジトリを作る権限があるか（第5回で手順書のリポジトリ、第6回で TODO アプリのリポジトリを作る）
- 受講者に Issue ラベルを作る権限があるか（第9回以降、ストーリーの Issue にタグ名のラベルを付ける）
- ブランチ保護（main への直接 push の禁止）は、第5回では講師が画面で見せるだけにした（講師用資料の「講師が見せる補足」）。GitHub の無料プランの非公開リポジトリでは使えず、GitLab ではプランによって設定できる範囲が違う

### Q5 mise・uv・PyPI へのアクセス

研修の環境構築では、次の通信が発生します。プロキシで止められていないかを、事前に講師が確認してください。

| 通信先 | 用途 |
| --- | --- |
| `mise.run`、`mise.jdx.dev` | mise のインストール |
| `github.com`、`objects.githubusercontent.com` | mise が Python（python-build-standalone）と uv を取得する |
| `pypi.org`、`files.pythonhosted.org` | uv がパッケージを取得する |
| `archive.ubuntu.com`、`security.ubuntu.com`、`esm.ubuntu.com` | apt（第2回）。`esm.ubuntu.com` は https で接続する |
| `untrusted-root.badssl.com` | 第2回の演習で、証明書エラーの見え方を確かめる |
| `jsonplaceholder.typicode.com` | 第3回の演習で、公開 API をプロキシ越しに呼ぶ（通らなければ講師の画面で見せる） |
| `registry.npmjs.org`、`nodejs.org` | 第4回で講師が見せる補足（mise で Node.js を入れる）と、資料の HTML 版・PDF 版を作る tools の docs タスクで使う |

htmx（第12回で講師が見せる補足）を CDN から読み込む場合は、その CDN（`unpkg.com` など）への通信も要ります。

### Q8 研修ディレクトリの配布

- 研修ディレクトリのルートは git 管理しない方針なので、配布は zip などのファイル共有になる想定
- 配る一式は `tools/` の `mise run dist -- <出力先>` で作る。`.git` はすべて含めず、各回の `instructor.md`（講師用）、`handoff.md`、`docs/_template/` も除く。HTML 版・PDF 版（`docs/_build/`）は含める
- 見本の TODO アプリ（`examples/todo-app/` と各回終了時点の `examples/todo-app-snapshots/session-NN/`）は git を使わない普通のフォルダなので、そのままコピーする。遅れた受講者はそのフォルダを `workspace/` にコピーして追いつく（[examples/README.md](../examples/README.md)）
- 見本にはコミット履歴がない。TDD の順序やコミットの分け方は、講師が画面で見せる

### Q10 Ubuntu のバージョンと WSL

- Ubuntu のバージョンによって sudo の実装が違い、`sudo -E` で環境変数を引き継げないことがある（第2回の資料を作るときに Ubuntu 26.04 の sudo-rs で確認）。第2回では `sudo --preserve-env=変数名` を使う形で書いている
- WSL が Windows のプロキシ設定を自動で引き継ぐ設定になっているかで、第2回の手順の一部が不要になる
