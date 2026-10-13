# コンフリクト解決の様子

演習の手順8を、講師がリモートの代わりにローカルのベアリポジトリを使って実際に実行した結果です（git 2.53）。PR のマージは `git merge --no-ff` で代用しています。コミットのハッシュは実行するたびに変わります。

## 状況

| ブランチ | Issue | 変更（README.md の1行目） | 状態 |
| --- | --- | --- | --- |
| `issue-1-target-env` | #1 | `# 環境構築手順` → `# 環境構築手順（WSL の Ubuntu 向け）` | PR #3 がマージ済み |
| `issue-2-duration` | #2 | `# 環境構築手順` → `# 環境構築手順（所要30分）` | PR #4 がコンフリクトでマージできない |

マージ前の `git log --oneline --graph --all`（2本とも同じ main から分かれている）:

```console
$ git log --oneline --graph --all
* 9ceab5e 手順書のタイトルに対象の環境を書く
| * 89a066b 手順書のタイトルに所要時間の目安を書く
|/
* 088f8f3 動作確認用の main.py を追加する
* 664855c Python と依存パッケージのバージョンを固定する
* c91eb74 第4回の環境構築手順書を追加する
* baae486 .venv と .env を Git の管理から外す
```

## 1. 最新の main を取り込む

```console
$ git switch issue-2-duration
Switched to branch 'issue-2-duration'
Your branch is up to date with 'origin/issue-2-duration'.
$ git fetch origin
$ git merge origin/main
Auto-merging README.md
CONFLICT (content): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
```

`git fetch origin` は、ホスティングで PR をマージした場合、`main -> origin/main` の更新を表示します。

## 2. 状況を確かめる

```console
$ git status
On branch issue-2-duration
Your branch is up to date with 'origin/issue-2-duration'.

You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   README.md

no changes added to commit (use "git add" and/or "git commit -a")
```

## 3. 解決前のファイル（先頭）

```text
<<<<<<< HEAD
# 環境構築手順（所要30分）
=======
# 環境構築手順（WSL の Ubuntu 向け）
>>>>>>> origin/main

WSL の Ubuntu に mise と uv を入れ、`mise run hello` が動くところまでの手順です。
```

- `<<<<<<< HEAD` から `=======` まで: 今いるブランチ（`issue-2-duration`、#2）の内容
- `=======` から `>>>>>>> origin/main` まで: 取り込もうとした main（PR #3 で入った #1）の内容

## 4. 解決後のファイル（先頭）

#1（対象の環境を書く）と #2（所要時間を書く）の両方の目的を成り立たせ、記号の行を消しました。

```text
# 環境構築手順（WSL の Ubuntu 向け・所要30分）

WSL の Ubuntu に mise と uv を入れ、`mise run hello` が動くところまでの手順です。
```

`git diff` で、両方の変更が合わさったことを確かめられます（左の2列が、それぞれのブランチから見た変更を表します）。

```console
$ git diff
diff --cc README.md
index 8f797f5,137bcea..0000000
--- a/README.md
+++ b/README.md
@@@ -1,4 -1,4 +1,4 @@@
- # 環境構築手順（所要30分）
 -# 環境構築手順（WSL の Ubuntu 向け）
++# 環境構築手順（WSL の Ubuntu 向け・所要30分）

  WSL の Ubuntu に mise と uv を入れ、`mise run hello` が動くところまでの手順です。

```

## 5. コミットして push し、PR をマージする

```console
$ grep -n '^<<<<<<<\|^=======\|^>>>>>>>' README.md
$ git add README.md
$ git commit --no-edit
[issue-2-duration a19a263] Merge remote-tracking branch 'origin/main' into issue-2-duration
$ git push
To <リポジトリのURL>
   89a066b..a19a263  issue-2-duration -> issue-2-duration
```

`grep` が何も出力しないことで、記号の消し忘れがないことを確かめています。この後、PR #4 の差分をもう一度セルフレビューしてからマージすると、Issue #2 が閉じます。

## 6. 手元の main をそろえる

```console
$ git switch main
$ git pull
$ head -1 README.md
# 環境構築手順（WSL の Ubuntu 向け・所要30分）
$ git log --oneline --graph
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

## よくない解決

| 解決 | 何が困るか |
| --- | --- |
| `# 環境構築手順（所要30分）` だけ残す | #1 の目的（対象の環境）が失われる。#1 は PR #3 で「完了」として閉じたのに、main から消える |
| `# 環境構築手順（WSL の Ubuntu 向け）` だけ残す | #2 の目的が失われたまま、PR #4 のマージで #2 が閉じてしまう |
| 記号の行を残したまま `git add` | Git は記号が残っていても add・commit できる。手順書がそのまま壊れる |
| ついでにタイトルを全く別の名前にする | どちらの Issue にも書かれていない変更。やりたければ新しい Issue にする |
