# 第5回 Git と GitHub
tag: git-基礎, git-github, 標準, test-レビュー
前提タグ: linux-ファイル, linux-アプリ, env-mise, env-python
所要: 座学15分 / ハンズオン45分

## ゴール

- 作業ツリー・ステージ・リポジトリ・リモートの4つの場所と、`add`・`commit`・`push` でファイルがどう移るかを説明できる
- `.gitignore` を先に書き、目的ごとの小さなコミットに「何を・なぜ」のメッセージを付けられる
- main を直接触らず、Issue → ブランチ → PR → セルフレビュー → マージの流れで変更を入れ、マージで Issue を閉じられる
- 2本のブランチが同じ行を変えたコンフリクトを、両方の目的が成り立つ形で解決できる

## 事前準備

- 第4回のハンズオンで作った一式が `~/handsoff/workspace/session04/` にある（`README.md`・`mise.toml`・`pyproject.toml`・`uv.lock`・`main.py`）
- `<Gitホスティング>` のアカウントと、push に使うトークン。講師が案内する（[open-questions.md](../open-questions.md) の Q4）
- 社内ネットワークでは、第2回の手順6で入れたプロキシの環境変数が `~/.bashrc` にある。git は環境変数を読むので、git の設定は要らない（Q1）

## まとめ

冒頭の座学で使います。ハンズオンでは、第4回の環境構築手順書をリポジトリにし、Issue からマージまでを1人で2回通します。

### 4つの場所

| 場所 | ひとことで | 次の場所へ | 中を見る | 参照（Pro Git） |
| --- | --- | --- | --- | --- |
| 作業ツリー | 編集しているファイル | `git add` | `git status`・`git diff` | 1.3、2.2 |
| ステージ | 次のコミットに入れるもの。変更の一部だけを選べる | `git commit` | `git diff --staged` | 2.2 |
| リポジトリ（`.git/`） | コミットの履歴 | `git push` | `git log` | 2.3 |
| リモート（`origin`） | `<Gitホスティング>` 上のリポジトリ。Issue と PR もここ | `git fetch`・`git pull` で手元へ | `git branch -a` | 2.5、3.5 |

### コマンド

| コマンド | 意味 | 参照（Pro Git） |
| --- | --- | --- |
| `git config --global 名前 値` | 全リポジトリで使う設定（`~/.gitconfig`） | 1.6 |
| `git init` | **今いるディレクトリ**をリポジトリにする（`.git/` を作る） | 2.1 |
| `git status`・`git status --short` | どのファイルがどの場所にあるか。迷ったらこれ | 2.2 |
| `git add ファイル`・`git commit -m "何を" -m "なぜ"` | ステージに載せる／記録する。2つ目の `-m` が本文 | 2.2 |
| `git diff`・`git diff --staged` | 作業ツリーとステージ／ステージと最新のコミットの差分 | 2.2 |
| `git restore ファイル` | 作業ツリーの変更を捨て、最新のコミットに戻す | 2.4 |
| `git log --oneline --graph --all` | 履歴を1行ずつ、分岐と合流を線で | 2.3、3.2 |
| `git remote add origin URL`・`git push -u origin 名前` | リモートを登録する／ブランチを初めて送る | 2.5 |
| `git switch -c 名前`・`git switch 名前` | ブランチを作って移る／移る | 3.2 |
| `git fetch origin`・`git merge origin/main` | リモートの最新を取る／今のブランチに取り込む | 3.2、3.5 |
| `git merge --abort` | マージを途中でやめ、マージの前に戻す | 3.2 |
| `git pull`・`git branch -d 名前` | fetch ＋ merge／マージ済みのブランチを消す | 2.5、3.2 |

### Issue・ブランチ・PR

| 用語 | ひとことで | 参照 |
| --- | --- | --- |
| Issue | やること。目的と完了条件を書く | Pro Git 6.2 |
| ブランチ | コミットを指す名前。main から分けて、main を壊さずに作業する | Pro Git 3.1 |
| PR | ブランチの変更を main に入れる提案とレビューの場（GitLab では Merge Request） | Pro Git 6.2 |
| `Closes #1` | PR の本文に書くと、マージで Issue #1 が閉じる（GitHub・GitLab 共通） | Pro Git 6.2 |
| セルフレビュー | マージの前に、自分の PR の差分を他人のつもりで読む | SE基礎 2章・3章 |
| コンフリクト | 2本のブランチが同じ箇所（隣の行を含む）を変え、Git が自動でまとめられない状態 | Pro Git 3.2 |

### 判断の基準（[研修の規約](assets/commit-convention.md)）

| 場面 | 基準 | 参照 |
| --- | --- | --- |
| コミット | 1コミット1目的。1行目＝何を（〜する）、本文＝なぜ（差分を見てもわからないこと） | Pro Git 5.2 |
| 入れないもの | `.venv/` と秘密情報（`.env`）。**add の前に** `.gitignore` に書く | Pro Git 2.2 |
| ブランチ | main に直接コミットしない（作った直後の数コミットだけ例外）。1 Issue = 1 ブランチ `issue-<番号>-<内容>` | Pro Git 3.4 |
| PR の本文 | 目的（`Closes #番号`）・変更点・確認方法（[テンプレート](../templates/pull_request.md)） | Pro Git 6.2 |
| セルフレビュー | 目的・確認方法・読みやすさ・履歴・安全を見て、確かめたことをコメントに残す | SE基礎 2章・3章 |
| コンフリクト | **どちらかを選ばず、両方の目的が成り立つ形**にする。記号の行（`<<<<<<<`・`=======`・`>>>>>>>`）はすべて消す | Pro Git 3.2 |
| 第6回から | アプリのリポジトリ（`workspace/todo-app/`）でも、変更は同じ流れ（Issue → ブランチ → PR → セルフレビュー → マージ）で入れる | — |

## ハンズオン

1ステップ1コマンド。各ステップは「🖋 やること → 📚 参考書・公式資料の節 → 📒 説明 → コマンド」。作業場所は `~/handsoff/workspace/session05/`（手順書のリポジトリ）。見本は [examples/session05/](../../examples/session05/README.md)。ブラウザで行うステップは、GitHub の画面の名前で書き、GitLab の名前を括弧に入れる。

### 1. Git の設定（3分）

#### 🖋 Git の版を見る

📒 `git switch` は 2.23 以降、`init.defaultBranch` は 2.28 以降で使える

```sh
git --version
```

#### 🖋 名前とメールアドレスを設定する

📚 Pro Git 1.6 最初のGitの構成

📒 名前とメールアドレスは、コミットごとに作者として記録される。`--global` はホームの `~/.gitconfig` に書き、全リポジトリで使う

```sh
git config --global user.name "自分の名前（ローマ字）"
git config --global user.email "<Gitホスティング> に登録したメールアドレス"
```

#### 🖋 ブランチ名・改行・日本語・エディタを設定する

📒 最初のブランチを main にし、改行を LF にそろえ、日本語のファイル名を化けさせない。エディタは、マージコミットのメッセージを書くときなどに開く

```sh
git config --global init.defaultBranch main
git config --global core.autocrlf input
git config --global core.quotepath false
git config --global core.editor nano
```

#### 🖋 設定を確かめる

```sh
git config --global --list   # 6行が出る
```

### 2. リポジトリを作る（4分）

#### 🖋 作業場所に移る

📒 `git init` は今いるディレクトリをリポジトリにする。`~` や `~/handsoff` で打つと、ホームや研修ディレクトリ全体が対象になるので、必ず `pwd` で確かめる

```sh
cd ~/handsoff/workspace/session05; pwd
```

#### 🖋 第4回の一式をコピーする

📒 `.venv` は渡さないもの（第4回の手順6）なのでコピーしない。作業場所の案内の `README.md` は、手順書で上書きしてよい

```sh
cp ../session04/{README.md,mise.toml,pyproject.toml,uv.lock,main.py} .
```

#### 🖋 mise.toml を信頼して .venv を作る

📒 コピーした `mise.toml` はまだ信頼されていない（第4回の手順6）。中身を見てから信頼し、手順書の「3. 依存パッケージを入れる」で `.venv` を作る

```sh
cat mise.toml; mise trust; mise run setup
```

#### 🖋 リポジトリにする

📚 Pro Git 2.1 Gitリポジトリの取得

📒 `git init` は `.git/` を作る。履歴と設定はすべてここに入る。リポジトリにするのは `session05` だけで、`workspace/` と `~/handsoff` は Git で管理しない

```plantuml
@startwbs
* &#126;/handsoff/workspace\nGit で管理しない
** mise.toml
** session04\n第4回の一式
** session05\nリポジトリ
*** .git/\n履歴と設定
*** README.md ほか\n第4回のコピー
*** .venv/\nリポジトリに入れない
@endwbs
```

```sh
git init; ls -a
```

#### 🖋 状態を見る

📚 Pro Git 2.2 変更内容のリポジトリへの記録

📒 まだ何も記録していないので、ファイルはすべて「追跡されていない（Untracked）」。迷ったらまず `git status`

```sh
git status   # On branch main / No commits yet
```

### 3. 先に .gitignore を書く（5分）

#### 🖋 .venv が出てこない理由を見る

📒 uv が作る `.venv` には `*` だけを書いた `.gitignore` が入っており、`.venv` の中身はすべて無視される。`python -m venv`（3.12）で作ると入らないので、リポジトリの `.gitignore` にも書く

```sh
cat .venv/.gitignore   # *
```

#### 🖋 秘密情報のファイルを置く

📒 `.env` は秘密情報を書くことが多いファイル名。ここではダミーを置き、`git status` に出ることを見る

```sh
echo 'HTTP_PROXY=http://user:password@proxy.example.com:8080' > .env; git status --short   # ?? .env
```

#### 🖋 .gitignore を書く

📚 Pro Git 2.2 変更内容のリポジトリへの記録（ファイルの無視）

📒 一度コミットしたファイルは、後で `.gitignore` に書いても過去のコミットに残る。そのため add より先に書く

```sh
nano .gitignore
```

```gitignore
# 仮想環境（mise.toml と uv.lock から作り直せる）
.venv/
# Python が実行時に作るファイル
__pycache__/
# 秘密情報
.env
```

#### 🖋 .env が消えたのを見る

📒 `git check-ignore -v` は、どのファイルの何行目で無視されたかを出す

```sh
git status --short; git check-ignore -v .env .venv
```

#### 🖋 .gitignore だけを最初にコミットする

📚 Pro Git 5.2 プロジェクトへの貢献（コミットのガイドライン）

📒 1行目に「何を」、2つ目の `-m`（本文）に「なぜ」を書く

```sh
git add .gitignore; git commit -m ".venv と .env を Git の管理から外す" -m "仮想環境は作り直せ、.env には秘密情報が入るため。"
```

- 確かめたら `rm .env`

> 座学: add の前に `.gitignore` を書く理由（→ まとめ「判断の基準」）

### 4. 目的ごとにコミットする（7分）

#### 🖋 手順書をステージに載せる

📚 Pro Git 1.3 Gitの基本、2.2 変更内容のリポジトリへの記録

📒 `add` で作業ツリーからステージへ、`commit` でステージからリポジトリへ移す。2段階なので、変更の一部だけをコミットできる

```mermaid
flowchart LR
  W["作業ツリー<br/>編集中のファイル"] -- "git add" --> S["ステージ<br/>次のコミット"]
  S -- "git commit" --> R["リポジトリ<br/>.git/ の履歴"]
  R -- "git push" --> O["リモート<br/>origin"]
  W -. "git diff" .- S
  S -. "git diff --staged" .- R
```

```sh
git add README.md; git status --short   # A  README.md
```

#### 🖋 これからコミットする中身を見る

```sh
git diff --staged | head -20
```

#### 🖋 手順書をコミットする

📒 1行目は「〜する」の形で、そのコミットを入れると何が起きるかを書く（[規約](assets/commit-convention.md)の2）

```sh
git commit -m "第4回の環境構築手順書を追加する"
```

#### 🖋 版を固定するファイルをまとめてコミットする

📒 3つのファイルで1つの目的（版の固定）なので、1つのコミットにする

```sh
git add mise.toml pyproject.toml uv.lock
git commit -m "Python と依存パッケージのバージョンを固定する" -m "README の手順どおりに進めれば、誰の PC でも同じバージョンになるようにする。"
```

#### 🖋 残りをコミットする

```sh
git add main.py; git commit -m "動作確認用の main.py を追加する"
```

#### 🖋 履歴を見る

📚 Pro Git 2.3 コミット履歴の閲覧

📒 コミットは1つ前のコミットを指してつながる。`git log --oneline` の1行目だけで、何をしたかがわかるようにする

```sh
git log --oneline; git status   # nothing to commit, working tree clean
```

#### 🖋 間違えた変更を入れる

📚 Pro Git 2.4 作業のやり直し

📒 コミットした後のファイルは、編集すると「変更あり」になる。`add` する前なら、`git restore` で最新のコミットの状態に戻せる

```mermaid
flowchart LR
  u["未追跡"] -- "git add" --> s["ステージ済み"]
  s -- "git commit" --> c["変更なし"]
  c -- "編集" --> m["変更あり"]
  m -- "git add" --> s
  m -- "git restore" --> c
```

```sh
echo 'まちがい' >> README.md; git diff
```

#### 🖋 最新のコミットの状態に戻す

```sh
git restore README.md; git status
```

### 5. リモートに push する（4分）

#### 🖋 空のリポジトリを作る（ブラウザ）

📒 `<Gitホスティング>` に非公開のリポジトリ `session05` を作る。README などの初期ファイルを付けると、手元にないコミットができて push が拒否されるので、何も付けない

#### 🖋 リモートを登録する

📚 Pro Git 2.5 リモートでの作業

📒 `origin` はリモートの URL に付ける別名

```sh
git remote add origin <リポジトリのURL>; git remote -v
```

#### 🖋 push する

📒 ユーザー名とパスワードを聞かれたら、パスワードにはトークンを入れる。`-u` で手元の main とリモートの main を結び付け、次からは `git push` だけで送れる

```sh
git push -u origin main
```

#### 🖋 リモートのブランチを見る

📚 Pro Git 3.5 リモートブランチ

📒 `origin/main` は、最後にリモートとやり取りしたときのリモートの main を、手元に記録したもの

```sh
git branch -a; git status   # up to date with 'origin/main'
```

- 確認: ブラウザでファイルと4つのコミットが見える

### 6. Issue を立て、ブランチを2本作る（8分）

#### 🖋 Issue を2つ立てる（ブラウザ）

📚 Pro Git 6.2 プロジェクトへの貢献

📒 Issue の本文には、目的と完了条件を1行ずつ書く。2つとも README.md の1行目の末尾を変えるので、後でコンフリクトが起きる

| Issue | タイトル | 目的 | 完了条件 |
| --- | --- | --- | --- |
| #1 | 手順書のタイトルに対象の環境を書く | 読んでよい手順書かを最初の行で判断できる | 1行目の末尾に `（WSL の Ubuntu 向け）` |
| #2 | 手順書のタイトルに所要時間の目安を書く | 始める前に作業の時間を確保できる | 1行目の末尾に `（所要30分）` |

#### 🖋 1本目のブランチを作る

📚 Pro Git 3.1 ブランチとは

📒 ブランチはコミットを指す名前。`HEAD` は今いるブランチを指し、コミットすると今いるブランチだけが進む

```sh
git switch -c issue-1-target-env
```

#### 🖋 1行目を変える

```sh
sed -i '1s/$/（WSL の Ubuntu 向け）/' README.md; git diff   # nano で直してもよい
```

#### 🖋 コミットする

📒 `-a` は、追跡しているファイルの変更をまとめて add する

```sh
git commit -am "手順書のタイトルに対象の環境を書く" -m "読んでよい手順書かを最初の行で判断できるようにする。"
```

#### 🖋 1本目を push する

📒 GitHub では、push の出力に PR を作る URL が出る

```sh
git push -u origin issue-1-target-env
```

#### 🖋 main に戻る

📒 2本目は必ず main から作る。1本目の上に作ると、2本目に1本目の変更が入り、コンフリクトも起きない

```sh
git switch main; head -1 README.md   # # 環境構築手順 のまま
```

#### 🖋 2本目のブランチで同じ行を変える

```sh
git switch -c issue-2-duration; sed -i '1s/$/（所要30分）/' README.md
```

#### 🖋 2本目をコミットして push する

```sh
git commit -am "手順書のタイトルに所要時間の目安を書く" -m "始める前に作業の時間を確保できるようにする。"
git push -u origin issue-2-duration
```

#### 🖋 分かれ方を見る

📚 Pro Git 3.2 ブランチとマージの基本

📒 2本とも同じ main のコミットから分かれている。分かれ方が違ったら講師を呼ぶ。図ではブランチ名を `issue-1`・`issue-2` と略す

```mermaid
gitGraph
  commit id: ".gitignore"
  commit id: "手順書"
  commit id: "版の固定"
  commit id: "main.py"
  branch issue-1
  commit id: "対象の環境"
  checkout main
  branch issue-2
  commit id: "所要時間"
```

```sh
git log --oneline --graph --all
```

### 7. PR を出し、セルフレビューして1本目をマージする（6分）

#### 🖋 PR を2つ作る（ブラウザ）

📚 Pro Git 6.2 プロジェクトへの貢献

📒 「Compare & pull request」（GitLab は push の出力の URL）から作る。マージ先は `main`、本文は[テンプレート](../templates/pull_request.md)の目的・変更点・確認方法で書き、目的に `Closes #1`（2本目は `Closes #2`）を入れる

| PR | ブランチ | 目的に書く行 |
| --- | --- | --- |
| 1本目 | `issue-1-target-env` → `main` | `Closes #1` |
| 2本目 | `issue-2-duration` → `main` | `Closes #2` |

#### 🖋 手元でも PR の差分を見る

📒 `main...ブランチ` は、ブランチが main から分かれた後の変更だけを見せる。PR の「Files changed」（GitLab は「Changes」）と同じ差分になる

```sh
git diff main...issue-1-target-env
```

#### 🖋 セルフレビューする（ブラウザ）

📚 SE基礎 2章 コードを読む、3章 コードを書く

📒 「Files changed」で差分を他人のつもりで読み、確かめたことを `[確認]` で始まる行コメントに1件以上残す。観点は[規約](assets/commit-convention.md)の7（目的・確認方法・読みやすさ・履歴・安全）。自分の PR は承認（Approve）できない

#### 🖋 1本目をマージする（ブラウザ）

📒 「Merge pull request」（GitLab は「Merge」）で、既定のマージコミットでマージする。`Closes #1` で Issue #1 が閉じ、同じ行を変えた2本目の PR はコンフリクトの表示に変わる

- 確認: Issue #1 が Closed。2本目の PR に「This branch has conflicts」（GitLab は「Merge blocked」など）

#### 🖋 リモートの main を取ってくる

📚 Pro Git 3.5 リモートブランチ

📒 マージはリモートで起きたので、手元の `origin/main` は古いまま。`git fetch` でリモートの最新を取ってくる（手元の main は変わらない）

```mermaid
gitGraph
  commit id: "main.py"
  branch issue-1
  commit id: "対象の環境"
  checkout main
  branch issue-2
  commit id: "所要時間"
  checkout main
  merge issue-1 id: "1本目の PR"
```

```sh
git fetch origin; git log --oneline --graph --all
```

> 座学: PR の3項目とセルフレビューの観点（→ まとめ「判断の基準」／SE基礎 3章）

### 8. コンフリクトを解決して2本目をマージする（8分）

#### 🖋 2本目のブランチに main を取り込む

📚 Pro Git 3.2 ブランチとマージの基本（マージ時のコンフリクト）

📒 2本のブランチが同じ行を変えたので、どちらを残すかを Git は決められず、マージが途中で止まる

```sh
git switch issue-2-duration; git merge origin/main   # CONFLICT (content): Merge conflict in README.md
```

#### 🖋 状態を見る

📒 迷ったら `git merge --abort` で、マージの前に戻せる

```sh
git status   # both modified: README.md
```

#### 🖋 記号を読む

📒 `HEAD` から `=======` までが今のブランチ（#2）、`=======` から下が取り込んだ main（#1）の内容

```text
<<<<<<< HEAD
# 環境構築手順（所要30分）               ← 今のブランチ（#2）
=======
# 環境構築手順（WSL の Ubuntu 向け）     ← main に入った変更（#1）
>>>>>>> origin/main
```

```sh
head -5 README.md
```

#### 🖋 両方を成り立たせて直す

📒 片方だけ残すと、もう一方の Issue は閉じたのに目的が失われる。記号の行はすべて消す

```sh
nano README.md   # 1行目を「# 環境構築手順（WSL の Ubuntu 向け・所要30分）」にする
```

#### 🖋 記号が残っていないか確かめる

📒 Git は記号が残っていても add・commit できる。add の前に自分で確かめる

```sh
grep -n '^<<<<<<<\|^=======\|^>>>>>>>' README.md   # 何も出なければよい
```

#### 🖋 マージコミットを作って push する

📒 解決した結果は、2本目のブランチのマージコミットになる。push すると2本目の PR に加わり、コンフリクトの表示が消える

```mermaid
gitGraph
  commit id: "main.py"
  branch issue-1
  commit id: "対象の環境"
  checkout main
  branch issue-2
  commit id: "所要時間"
  checkout main
  merge issue-1 id: "1本目の PR"
  checkout issue-2
  merge main id: "解決"
```

```sh
git add README.md; git commit --no-edit; git push
```

#### 🖋 もう一度セルフレビューしてマージする（ブラウザ）

📒 2本目の PR の差分を読み直し、どう解決したかをコメントに残してからマージする。`Closes #2` で Issue #2 が閉じる

- 確認: Issue が2つとも Closed

#### 🖋 手元の main をそろえる

📚 Pro Git 2.5 リモートでの作業

📒 `git pull` は `git fetch` と `git merge` をまとめて行う

```sh
git switch main; git pull; head -1 README.md   # 両方の変更が入った1行
```

#### 🖋 済んだブランチを消す

📒 `-d` はマージ済みのブランチだけを消す。マージしていないと消さずに止まる

```sh
git branch -d issue-1-target-env issue-2-duration
```

#### 🖋 全体の履歴を見る

📒 最初の4つのコミットの後、main への変更はすべて PR のマージコミットを通っている。第6回からのアプリのリポジトリでも、この形を保つ

```mermaid
gitGraph
  commit id: "main.py"
  branch issue-1
  commit id: "対象の環境"
  checkout main
  branch issue-2
  commit id: "所要時間"
  checkout main
  merge issue-1 id: "1本目の PR"
  checkout issue-2
  merge main id: "解決"
  checkout main
  merge issue-2 id: "2本目の PR"
```

```sh
git log --oneline --graph
```

> 座学: コンフリクトは「両方を成り立たせる」。片方だけ残すと何が失われるか（→ まとめ「判断の基準」）

## 読む章

| 区分 | 資料 | 範囲 | 読み方 |
| --- | --- | --- | --- |
| 無料 | [Pro Git（日本語版）](https://git-scm.com/book/ja/v2) | 1章 使い始める、2章 Git の基本、3.1〜3.2・3.5 ブランチ、5.2 プロジェクトへの貢献、6.2 GitHub のプロジェクトへの貢献 | 該当章（ハンズオンの「参照」の節を中心に） |
| 無料 | 同上 | 2.4 作業のやり直し、3.6 リベース、7.7 リセットコマンド詳説 | 引く（取り消したいとき） |
| 参考書 | [ソフトウェアエンジニアリングの基礎](https://www.oreilly.co.jp/books/9784814401789/)（SE基礎） | 2章 コードを読む、3章 コードを書く | 通読（セルフレビューの観点。第7回でも使う） |
| 紹介（副読本） | [達人プログラマー 第2版](https://www.hanmoto.com/bd/isbn/9784274226298) | 基本ツール（バージョン管理） | 持っている人は通読（第1〜5回で基本ツールの範囲） |
| 紹介（副読本） | [リーダブルコード](https://www.oreilly.co.jp/books/9784873115658/) | 巻末解説の添削コミット | 持っている人は（セルフレビューの参考） |
