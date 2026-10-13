# 第5回 Git と GitHub（講師用）
tag: git-基礎, git-github, 標準, test-レビュー
前提タグ: linux-ファイル, linux-アプリ, env-mise, env-python
所要: 座学15分 / ハンズオン45分

<!-- 講師用。受講者に配るときはこのファイルを除く -->

## 進行メモ

各自が自分のリポジトリで「設定 → init → .gitignore → 目的ごとのコミット → push → Issue 2つとブランチ2本 → PR → セルフレビュー → 1本目をマージ → 2本目のコンフリクトを解決してマージ → Issue が閉じる」までを1人で通します。第6回以降はこの流れを前提にするので、手順8まで全員が終えることを優先します。

| 時刻 | 内容 | メモ |
| --- | --- | --- |
| 0:00 | 座学: まとめ（15分） | 「4つの場所」（4分）→「コマンド」（3分。ブランチ・PR は後半で全部体験すると予告する程度）→「Issue・ブランチ・PR」（3分）→「判断の基準」と[規約](assets/commit-convention.md)（5分）。`add` と `commit` が2段階になっている理由（一部だけをコミットできる）と、「main を直接触らない」の2点を強調する |
| 0:15 | ハンズオン 1 Git の設定（3分） | 事前に案内して済ませてある人は `git config --global --list` で6行を確かめるだけでよい。`user.email` はホスティングに登録したものにさせる（違うとコミットがアカウントに結び付かない） |
| 0:18 | ハンズオン 2 リポジトリを作る（4分） | `git init` の前に `pwd` を必ず確かめさせる。`mise run setup` がネットワークで止まる人は飛ばしてよい（`.venv` がないと手順3の最初のステップが空振りするだけ） |
| 0:22 | ハンズオン 3 .gitignore（5分） | `.venv` が最初から `git status` に出ないことに気づかせてから、`.venv/.gitignore` の `*` を見せる。`.env` が消える瞬間を全員で見る。終わったら「> 座学:」で add の前に `.gitignore` を書く理由を1分 |
| 0:27 | ハンズオン 4 目的ごとのコミット（7分） | 4つの場所の図と `git diff`／`git diff --staged` を結び付ける。`git restore` は「add の前なら戻せる」範囲に留める（ステージや履歴の取り消しは補足で見せる） |
| 0:34 | ハンズオン 5 push（4分） | 認証で止まった人は講師が個別に対応し、ほかの人は先へ進める。空のリポジトリで作っていない人は「つまずきやすい点」の `rejected` を見る |
| 0:38 | ハンズオン 6 Issue とブランチ2本（8分） | 2本目を作る前に `git switch main` を忘れると、2本目が1本目の上に乗り、コンフリクトが起きない。最後の `git log --oneline --graph --all` で、2本が同じコミットから分かれていることを全員に確かめさせる |
| 0:46 | ハンズオン 7 PR とセルフレビュー（6分） | PR の本文はテンプレートを貼って埋めさせる。1本目をマージした直後に、2本目の PR の表示が変わったことを全体で確認する。終わったら「> 座学:」で PR の3項目とセルフレビューの観点を1分 |
| 0:52 | ハンズオン 8 コンフリクトの解決（8分） | 今日の山場。記号の上下がどちらのブランチかを、`text` の図で講師が指して説明する。2〜3人に解決した1行と `git log --oneline --graph` を画面で見せてもらい、「> 座学:」で片方だけ残す解決がなぜ誤りかを全体で確かめる |

時間が押したら、手順4の `git restore` と手順7の「手元でも PR の差分を見る」を講師の画面だけにします。手順6のブランチ2本と手順8のコンフリクトの解決は削らないでください。手順8が終わらない人は `git merge --abort` で戻してから終え、次の回の前に講師と一緒に手順8だけを行います（ほかの人は不要）。

第5回は振り返り・宿題・発展課題を設けません。元の宿題（第4回の手順書の改善を Issue → ブランチ → PR → セルフレビュー → マージで閉じる）は、手順6〜8で同じ流れを2回通すので外しました。手順書の改善が残っている人は、以降も同じ流れでこのリポジトリに入れてよいと伝えます。元の発展課題（restore・revert・reset の違い、rebase、ブランチ保護、PR テンプレート）は「講師が見せる補足（任意）」に移しました。

### 事前に確認すること

- `<Gitホスティング>` が決まっているか、受講者のアカウントが発行済みで、各自がリポジトリを作れるか（[open-questions.md](../open-questions.md) の Q4）。未定なら下の「ホスティングが使えない場合の代替手順」で進める
- 社内ネットワークから `<Gitホスティング>` に HTTPS で push できるか（Q1・Q5）。git は `https_proxy` などの環境変数を読むので、第2回の手順6で入れた環境変数で通る（第2回で `git ls-remote` を試している）。git 用のプロキシ設定（`git config http.proxy`）は案内していない。SSH はプロキシで止められることが多いので、資料は HTTPS 前提
- 認証方式（トークンか SSH 鍵か、トークンをどこに保存させるか）。WSL で `credential.helper store` を使うとトークンが平文で `~/.git-credentials` に保存されるので、社内の規定を確かめてから案内する
- 手順1の `git config` を前の週に案内しておくと、当日の3分を手順8に回せる
- 受講者の git のバージョン（`git --version`）。`git switch`・`git restore` は 2.23 以降、`init.defaultBranch` は 2.28 以降
- 受講者が第4回の一式（`workspace/session04/` の `README.md`・`mise.toml`・`pyproject.toml`・`uv.lock`・`main.py`）を持っているか。README の1行目がテンプレートどおり `# 環境構築手順` であること（手順6の `sed` が1行目の末尾に足す）
- ホスティングの画面の名前（「Compare & pull request」「Files changed」「This branch has conflicts」など）は変わることがある。研修の前に一度、1人分の流れを画面で通しておく
- GitHub では Issue と PR の番号が共通なので、演習では Issue #1・#2、PR #3・#4 になる。GitLab では Issue は `#1`、Merge Request は `!1` と別の番号になる。どちらでも `Closes #1` で Issue が閉じる

### workspace の構成

[workspace/README.md](../../workspace/README.md) のとおり、この回の作業場所 `workspace/session05/` を手順書のリポジトリにします。

```text
workspace/session05/      ← 手順書のリポジトリ（第5回で git init）
├─ .git/
├─ .gitignore
├─ README.md               第4回の環境構築手順（作業場所の案内の README は上書きしてよい）
├─ mise.toml, pyproject.toml, uv.lock, main.py   第4回のコピー
└─ .venv/                  手順2の mise run setup で作る。リポジトリには入れない
```

- `workspace/session01〜04/` はリポジトリにしない。Git で管理するのは、履歴を残す意味があるもの（手順書・コード・設計書）だけ
- 第6回でアプリのリポジトリ `workspace/todo-app/` を作る。以降のコードと設計書はそちらで、この回と同じ流れ（Issue → ブランチ → PR → セルフレビュー → マージ）で管理する
- 研修ディレクトリのルート（`~/handsoff`）と `workspace/` 自体は Git で管理しない。`git init` をそこで実行させないよう、手順2で `pwd` を必ず確かめさせる

### ホスティングが使えない場合の代替手順

ローカルのベアリポジトリをリモートの代わりにすると、Git の部分（push・ブランチ・マージ・コンフリクト解決）は同じように体験できます。PR・Issue・セルフレビューの画面操作はできないので、PR の説明とセルフレビューのコメントは `notes/pr-3.md` などの Markdown に書かせ、「PR のマージ」は main での `--no-ff` マージで代用します。

```sh
cd ~/handsoff/workspace
git init --bare -b main session05-remote.git     # ホスティングの代わり（session05/ の外に置く）
cd session05
git remote add origin ../session05-remote.git    # 手順5の <リポジトリのURL> の代わり
git push -u origin main
```

手順7の「1本目をマージする」の代わりは次のとおりです。

```sh
git switch main
git merge --no-ff issue-1-target-env -m "Merge pull request #3 from trainee/issue-1-target-env"
git push origin main
```

手順8はそのまま行い、「もう一度セルフレビューしてマージする」は同じく `git switch main` → `git merge --no-ff issue-2-duration` → `git push` で代用します。この手順は講師が実際に実行し、資料と見本に載せた出力（`CONFLICT (content): ...` など）と同じものが出ることを確かめてあります（git 2.53）。

## つまずきやすい点

| 症状 | 原因 | 対処 |
| --- | --- | --- |
| `Author identity unknown` で commit できない | `user.name` / `user.email` を設定していない | 手順1の `git config` をやり直す |
| `git status` の日本語のファイル名が `"\344\275\234..."` になる | `core.quotepath` が既定の true | `git config --global core.quotepath false` |
| `git commit` で vim が開いて抜けられない | `-m` を付けず、`core.editor` も未設定 | `Esc` → `:q!` で中止。`core.editor nano` を設定する |
| ホームディレクトリ全体が `Untracked files` に出る | `~` で `git init` した | `pwd` で場所を確かめ、誤って作った `~/.git` を講師と一緒に消す |
| `cp` で `No such file or directory` | 第4回の一式の一部がない、または `session05` 以外で実行した | `pwd` と `ls ../session04`。ないファイルは飛ばし、ある分だけで進める |
| `cat .venv/.gitignore` で `No such file or directory` | 手順2の `mise run setup` が止まった、または `.venv` を `python -m venv` で作った | 先に進んでよい。リポジトリの `.gitignore` に `.venv/` を書くので結果は同じ |
| `.venv/` の大量のファイルがステージに入った | `.gitignore` を書く前に `git add .` した（`.venv/.gitignore` がない場合） | `git rm -r --cached .venv` で下ろし、`.gitignore` に書く |
| `.gitignore` に書いたのに `.env` が `modified` と出る | コミット済みのファイルには `.gitignore` が効かない | `git rm --cached .env`。過去のコミットには残るので、本物のパスワードならすぐ変えさせる |
| `git add mise.toml pyproject.toml uv.lock` が `pathspec ... did not match` | コピーしていないファイルがある | ある分だけ add する |
| push で `Authentication failed` | パスワードでの認証が使えない（GitHub はトークンが必要） | トークン（GitHub は Personal access token）を発行させる（Q4） |
| push で `Could not resolve host` やタイムアウト | プロキシの環境変数がない、または今のシェルに読み込まれていない | `env \| grep -i _proxy`。第2回の手順書の 3-1 を確かめ、`exec bash`（Q1） |
| push で `rejected ... (fetch first)` | リモートを README 付きで作った | 空のリポジトリで作り直すのが早い |
| 2本目の PR に1本目の変更まで入っている／コンフリクトが起きない | `git switch main` をせずに2本目を作った | `git log --oneline --graph --all` で分岐元を見せる。2本目を消して main から作り直す（`git switch main` → `git branch -D issue-2-duration` → 手順6の後半）。リモートの2本目も消すか、`git push -f` で置き換える |
| `Closes #1` と書いたのに Issue が閉じない | PR のタイトルにだけ書いた、またはマージ先が main でない | PR の本文に書く。マージ先を確かめる |
| 自分の PR を Approve できない | GitHub では自分の PR は承認できない | セルフレビューは行コメントか「Comment」で残せばよいと伝える |
| `git merge origin/main` で `Already up to date` と出てコンフリクトしない | 手順7の `git fetch origin` をしていない | `git fetch origin` をしてからもう一度 |
| マージ後もファイルに `<<<<<<<` が残ったまま push した | 記号を消し忘れた。Git は記号が残っていても add できる | `grep` で確かめてから add する習慣をつけさせる。直すコミットを足して再 push |
| `git commit --no-edit` を付けずにエディタが開いた | マージコミットのメッセージ編集 | nano は `Ctrl+O` → `Enter` → `Ctrl+X` で保存して終わる |
| `git branch -d` が `not fully merged` で止まる | PR をまだマージしていない、または `git pull` の前 | ブラウザでマージ済みかを確かめ、`git pull` してからもう一度。`-D` で消させない |
| `git pull` で `divergent branches` のヒントが出る | main で直接コミットしていた | 演習のルール違反。講師と一緒に `git log --oneline --graph --all` で状況を確かめる |

## 解答例

### 手順ごとの表示

講師が代替手順（ベアリポジトリ）で実行した結果です（git 2.53、作者は例示用の `trainee`。ハッシュは毎回変わる）。詳しい出力は [examples/session05/](../../examples/session05/README.md) にあり、受講者にも見せてよい。

| 手順 | コマンド | 表示 |
| --- | --- | --- |
| 1 | `git config --global --list` | `user.name=...`、`user.email=...`、`init.defaultbranch=main`、`core.autocrlf=input`、`core.quotepath=false`、`core.editor=nano` |
| 2 | `git status` | `On branch main`、`No commits yet`、`Untracked files:` に5ファイル（`.venv` は出ない） |
| 3 | `cat .venv/.gitignore` | `*` |
| 3 | `.gitignore` を書いた後の `git status --short` | `?? .gitignore` と5ファイル（`.env` が消える） |
| 3 | `git check-ignore -v .env .venv` | `.gitignore:6:.env	.env` と `.gitignore:2:.venv/	.venv` |
| 4 | `git log --oneline` | コミットが4つ（`.gitignore` が最初） |
| 4 | `git restore` の後の `git status` | `nothing to commit, working tree clean` |
| 5 | `git status` | `Your branch is up to date with 'origin/main'.` |
| 6 | `git switch main; head -1 README.md` | `# 環境構築手順` |
| 7 | `git fetch origin` | `088f8f3..1da6333  main       -> origin/main` |
| 8 | `git merge origin/main` | `CONFLICT (content): Merge conflict in README.md`、`Automatic merge failed; ...` |
| 8 | `git status` | `You have unmerged paths.`、`both modified:   README.md` |
| 8 | `git branch -d ...` | `Deleted branch issue-1-target-env (was ...)` が2行 |

手順8の解決後の README.md の1行目です。

```markdown
# 環境構築手順（WSL の Ubuntu 向け・所要30分）
```

- #1 の目的（対象の環境を書く）と #2 の目的（所要時間を書く）の両方が成り立っている
- 片方だけ残すのは誤り。もう一方の Issue の目的が失われるのに、Issue は「完了」で閉じてしまう
- タイトルを2行に分ける・本文に移すといった解決も、両方の目的が成り立っていればよい

最後の `git log --oneline --graph`（main に戻って `git pull` した後）の結果です。

```console
*   d8cef1a Merge pull request #4 from trainee/issue-2-duration
|\
| *   a19a263 Merge remote-tracking branch 'origin/main' into issue-2-duration
| |\
| |/
|/|
* |   1da6333 Merge pull request #3 from trainee/issue-1-target-env
|\ \
| * | 9ceab5e 手順書のタイトルに対象の環境を書く
|/ /
| * 89a066b 手順書のタイトルに所要時間の目安を書く
|/
* 088f8f3 動作確認用の main.py を追加する
* 664855c Python と依存パッケージのバージョンを固定する
* c91eb74 第4回の環境構築手順書を追加する
* baae486 .venv と .env を Git の管理から外す
```

座学で問う点の答えは次のとおりです。

- `.gitignore` を先に書くのは、`git add .` などで `.venv/` や `.env` を一度でもコミットに入れると、取り除く手間がかかり、秘密情報は履歴に残ってしまうから
- `git diff` は作業ツリーとステージ、`git diff --staged` はステージと最新のコミットを比べる

### PR とセルフレビュー

見本: [examples/session05/](../../examples/session05/README.md)（PR の説明・セルフレビュー・コンフリクト解決の例）。手順7の後に受講者にも見せる。

見るポイントは次のとおりです。

- コミットが目的ごとに分かれ、1行目が「何を」を表しているか。`修正`・`update`・ファイル名だけ、はその場で直させる（`git commit --amend` は push 前だけ）
- 理由が必要な変更（`.gitignore`、手順書の修正）に本文で「なぜ」が書かれているか
- `git log --oneline --graph` で、最初の4つのあとは main への直接コミットがなく、すべてマージコミット経由になっているか
- PR の本文に目的（`Closes #番号`）・変更点・確認方法がそろい、変更点が実際の差分と一致しているか。確認方法が他人にも実行できる手順になっているか
- セルフレビューのコメントが「確かめたこと」か「気づいたこと」を具体的に書いているか（「OK」だけは不可）
- `.venv/`、`.env`、`__pycache__/` が入っていないか（`git ls-files`）。手順書にプロキシの認証情報などが書かれていないか

### 講師が見せる補足（任意）

時間が余ったときに講師の画面で見せます。受講者の課題にはしません。**演習のリポジトリでは試さない**（`reset --hard` は変更を消す）。

```sh
mkdir -p ~/git-practice && cd ~/git-practice && git init
```

| コマンド | 何が変わるか | 履歴 | 使いどころ |
| --- | --- | --- | --- |
| `git restore ファイル` | 作業ツリーの変更を捨てる | 変わらない | 編集を間違えたので最後のコミットに戻したい（手順4） |
| `git restore --staged ファイル` | ステージから下ろす（変更は残る） | 変わらない | `add` するファイルを間違えた |
| `git revert コミット` | 打ち消すコミットを新しく作る | 増える | push 済みのコミットを取り消したい |
| `git reset --soft HEAD~1` | ブランチを1つ戻す。変更はステージに残る | 減る | push 前に直前のコミットをやり直したい |
| `git reset HEAD~1`（`--mixed`） | ブランチを戻す。変更は作業ツリーに残る | 減る | push 前にコミットを分け直したい |
| `git reset --hard HEAD~1` | ブランチを戻し、変更も捨てる | 減る | 直前のコミットごと捨てたい（戻せない） |

- 「push 済みのコミットを取り消すなら revert」。reset は履歴を書き換えるので、リモートと食い違う
- rebase: 手順8を `git rebase origin/main` でやり直すと、log が1本の線になる。記号の上下は merge と逆になる（`HEAD` 側が main の変更、下側が自分のコミット）。rebase はコミットを作り直すので、push 済みのブランチには `git push --force-with-lease` が要る。「自分しか使っていないブランチでだけ rebase する」と伝える
- ブランチ保護: main への直接 push を禁止し、拒否されるのを見せる（GitHub: Settings → Rules → Rulesets／GitLab: Settings → Repository → Protected branches）。GitHub の無料プランの非公開リポジトリでは使えないので、講師のリポジトリで見せる（Q4）。拒否の文面はホスティングで違う（GitHub は `protected branch hook declined` など、GitLab は `You are not allowed to push code to protected branches on this project.` など）
- PR テンプレート: `.github/pull_request_template.md`（GitLab は `.gitlab/merge_request_templates/Default.md`）に [docs/templates/pull_request.md](../templates/pull_request.md) を置くと、新しい PR の本文に自動で入る。第6回のアプリのリポジトリで使ってよい

## 評価の観点

- 評価の観点「構成管理」（コミットの粒度とメッセージ、PR の説明とセルフレビュー）の最初の回。点数よりも、悪い例を個別にコメントして直させることを優先する
- `.gitignore` が最初のコミットにあり、`.venv/` と秘密情報が履歴に一度も入っていないか
- main を直接触らず、Issue → ブランチ → PR → セルフレビュー → マージの流れで変更が入っているか。Issue が PR のマージで閉じているか
- コンフリクトを、両方の Issue の目的を確かめて解決できたか

## カリキュラムとの関係（報告事項）

- 2026-10-12 の改訂で、旧第4回（Git の基本）と旧第5回（ブランチとプルリクエスト）を1回にまとめ、1人で2本のブランチを作ってコンフリクトを起こす形にした。受講者どうしのレビューはせず、セルフレビューにした。PR を講師が見る場合は、講師をリポジトリのメンバーに招待させる（権限は Q4 で確認）
- 2026-10-13 の見直しで、所要を座学15分 / ハンズオン45分にし、振り返り・宿題・発展課題をなくした。Git の初期設定は事前準備からハンズオンの手順1に移した。第4回の一式は第4回のハンズオンで作るので、事前準備は「手元にある」ことの確認だけにした
- 手順2で `mise trust` と `mise run setup` をして `.venv` を作るようにした。uv の `.venv` は自分の中の `.gitignore` で無視されるので、旧資料のダミーの `.venv/dummy` はやめ、`.env` で `.gitignore` の効き目を見せる形にした
- `git restore`（手順4）、`git branch -d`（手順8）、`git diff main...ブランチ`（手順7）をハンズオンに足した。revert・reset・rebase・ブランチ保護・PR テンプレートは「講師が見せる補足（任意）」にした
- 旧資料の「第2回の `git config --global http.proxy`」は誤りだった。第2回では git の設定はしておらず、プロキシの環境変数で通る
