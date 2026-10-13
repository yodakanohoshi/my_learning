# 第6回 Python の基本（講師用）
tag: python-構文
前提タグ: env-python, git-基礎, git-github
所要: 座学15分 / ハンズオン45分

<!-- 講師用。受講者に配るときはこのファイルを除く -->

## 進行メモ

各自が「REPL で書き方を試す → アプリのリポジトリ `todo-app` を作る → 雛形の関数を順に書く → main に push → `--due`・`list --overdue` を Issue → ブランチ → PR → セルフレビュー → マージで入れる」までを通します。第7回以降はこのリポジトリ（main に `todo.py`・`mise.toml`・`pyproject.toml`・`uv.lock`・`.gitignore`、`<Gitホスティング>` に push 済み）を前提にするので、手順6の push までは全員が終えることを優先します。

| 時刻 | 内容 | メモ |
| --- | --- | --- |
| 0:00 | 座学: まとめ（15分） | 「書き方」の表（7分）は REPL で数行打って見せる程度にし、全部を覚えさせない。「JSON と Python の対応」（2分）は `tasks.json` の見本を画面に出して対応を指す。「TODO の CLI」（2分）で今日のゴールを見せ、「判断の基準」（4分）は `except:` だけにしないことと、操作と表示を分けることの2点を強調する |
| 0:15 | ハンズオン 1 REPL（4分） | `KeyError` を必ず全員に出させる。終わりの「> 座学:」で `get` の使いどころ（後から足したキー。手順7で実際に効く）を1分 |
| 0:19 | ハンズオン 2 リポジトリを作る（5分） | `git init` の前に `pwd` を確かめさせる。`package = false` は「今日は1ファイルをそのまま動かす。第7回でパッケージにして消す」とだけ伝える |
| 0:24 | ハンズオン 3 雛形を読む（4分） | `main` の図を指しながら、`match` の各 `case` からどの関数が呼ばれるかをたどる。トレースバックは最後の行から読むことを、ここで一度見せる |
| 0:28 | ハンズオン 4 読み込みと保存（7分） | 講師の画面で一緒に書く。`with` を抜けると閉じることと、`FileNotFoundError` だけを捕まえる理由を説明する |
| 0:35 | ハンズオン 5 add・list・done（8分） | `cat tasks.json` で中身を見せ、`True` が `true` になっていることを確かめる。`mark_done` の図で「for の変数はリストの中身そのもの」を押さえる |
| 0:43 | ハンズオン 6 エラーと push（4分） | 終了コード 1（自分で返した）と 2（argparse）の違いを `echo $?` で見る。push の認証で止まった人は個別に対応し、ほかの人は手順7へ進める。「> 座学:」は1分 |
| 0:47 | ハンズオン 7 期限を足す（8分） | 変更が多いので、コードは資料からコピーさせてよい（HTML 版のコピーボタン）。`format_task` の引数が増えたので、`main` を置き換え忘れると `TypeError` になる。最後に手順5のタスク（`due` のキーがない）がそのまま表示されることを全員で確かめる |
| 0:55 | ハンズオン 8 PR とマージ（5分） | PR の本文はテンプレートを貼って埋めさせる。確認方法に手順7のコマンドを書かせる。時間がなければセルフレビューのコメントを1件にしてマージまで進める |

時間が押したら、手順1の f-string と手順4の「変換の結果を見る」を講師の画面だけにします。手順8のマージが授業中に終わらなかった人は、第7回の前に済ませるよう伝えます（PR まで出してあれば、第7回の冒頭でマージしてから始められます）。

第6回は振り返り・宿題・発展課題を設けません。元の宿題（`--due` と `list --overdue`、アプリのリポジトリの作成と push）は、手順2・6・7・8でハンズオンに入れました。リポジトリの作成を手順2に置き、機能の追加を第5回と同じ Issue → ブランチ → PR → セルフレビュー → マージの流れで入れることで、第5回の流れをアプリのリポジトリでもう一度通します。元の発展課題（EAFP と LBYL、ジェネレータ、`sys.argv` の直接のパターンマッチ）は「講師が見せる補足（任意）」に移しました。

### 事前に確認すること

- 受講者の `~/handsoff/workspace` で `python --version` が 3.12 になるか（`workspace/mise.toml`。第4回で mise を入れていない人は、手順1だけ `python3` で代用してよい）
- 受講者が `<Gitホスティング>` に新しい非公開リポジトリを作れ、push の認証が通るか（[open-questions.md](../open-questions.md) の Q4。第5回で通っていれば同じでよい）
- 雛形 `assets/todo_starter.py` は、模範の [session-06/todo.py](../../examples/todo-app-snapshots/session-06/todo.py) から期限の部分（`--due`・`--overdue`）を除き、関数の中身を `raise NotImplementedError("手順Nで書く")` にしたもの。手順4・5のコードを入れると手順6の状態、手順7のコードまで入れると、模範と冒頭の説明文（docstring とコメント）以外が同じになる
- `examples/todo-app-snapshots/session-06/` の `.gitignore`・`mise.toml`・`pyproject.toml`・`uv.lock` を手順2でコピーする。この4つを変えたら、資料の手順2の説明（`package = false`、`.gitignore` の中身）も直す

### workspace の構成

```text
workspace/todo-app/       ← アプリのリポジトリ（第6回で git init。第7〜12回もここ）
├─ .git/
├─ .gitignore              .venv/・__pycache__/・tasks.json
├─ mise.toml, pyproject.toml, uv.lock   見本のコピー（依存パッケージなし、package = false）
├─ todo.py                 雛形から書いたもの
├─ tasks.json              自分のデータ。コミットしない
└─ .venv/                  コミットしない
```

- 模範の `session-06/` には `README.md`（使い方）もあるが、ハンズオンでは作らない。アプリの README は第7回以降で書く
- GitHub では Issue と PR の番号が共通なので、手順7の Issue が #1、手順8の PR が #2 になる。GitLab では Merge Request は `!1`。どちらでも `Closes #1` で Issue が閉じる

## つまずきやすい点

| 症状 | 原因 | 対処 |
| --- | --- | --- |
| `NotImplementedError: 手順4で書く` | まだ書いていない関数が呼ばれた | 正常。手順4から順に中身を書く。手順4の時点で `list` が動くのは、タスクが0件で `format_task` が呼ばれないため |
| `IndentationError` / `unexpected indent` | 字下げのずれ、タブと空白の混在 | 空白4つにそろえる。関数の中は1段、`with`・`for`・`try` の中はもう1段 |
| `TypeError: 'NoneType' object is not iterable` | `load_tasks` の最後の `return tasks` がなく、`None` を返した | `except` の `return []` と最後の `return tasks` の両方があるか |
| `json.decoder.JSONDecodeError` | `tasks.json` が空や途中で壊れた（手で編集した、保存中に止めた） | `rm tasks.json` でやり直す。扱い方は「講師が見せる補足」の EAFP と LBYL |
| 日本語が `\u725b\u4e73` と保存される | `ensure_ascii=False` がない | 付ける。読み込みはどちらでも動くことも見せる |
| `done 1` しても `list` で `[未着手]` のまま | `save_tasks` の中身がない、または別のディレクトリで実行して別の `tasks.json` を見ている | `pwd` を確かめる。`Path("tasks.json")` は打ったディレクトリからの相対パス |
| 手順7の後に `TypeError: format_task() missing 1 required positional argument: 'today'` | `format_task` を変えたが `main` を置き換えていない | 手順7の `main` に置き換える |
| 手順7の後に `NameError: name 'date' is not defined` | `from datetime import date` を足していない | import の行に足す |
| 手順7の後に `KeyError: 'due'` | `task["due"]` で読んでいる | `task.get("due")` にする（手順5のタスクには `due` のキーがない） |
| `list --overdue` に期限が今日のタスクが出る | `<=` で比べている | 期限の当日はまだ期限切れでない。`<` にする |
| `git status` に `tasks.json` が出る | `.gitignore` をコピーしていない、または別の名前で保存した | `ls -a` で `.gitignore` を確かめ、`git check-ignore -v tasks.json` |
| `git push` で `rejected`（fetch first） | リポジトリを README 付きで作った | 第5回のつまずきやすい点と同じ。`git pull --rebase origin main` してから push するか、空のリポジトリで作り直す |
| `mise.toml` が `not trusted` と出る | コピーした `mise.toml` をまだ信頼していない | 中身を見て `mise trust` |

## 解答例

### 手順6の時点の実行例

```text
$ python todo.py add "牛乳を買う"
追加しました:   1 [未着手] 牛乳を買う
$ python todo.py done 1
完了にしました:   1 [完了] 牛乳を買う
$ python todo.py add "   "; echo $?
タイトルは1〜100文字で指定してください
1
$ python todo.py done 99; echo $?
タスクが見つかりません: 99
1
$ python todo.py done abc; echo $?
usage: todo.py done [-h] id
todo.py done: error: argument id: invalid int value: 'abc'
2
```

### 手順7の実行例

手順5で「牛乳を買う」「報告書を書く」を足し、1を完了にした後の例です。

```text
$ python todo.py add "レポートを出す" --due 2026-04-01
追加しました:   3 [期限切れ] レポートを出す（期限 2026-04-01）
$ python todo.py list
  1 [完了] 牛乳を買う
  2 [未着手] 報告書を書く
  3 [期限切れ] レポートを出す（期限 2026-04-01）
  4 [未着手] 本を返す（期限 2030-03-31）
$ python todo.py list --overdue
  3 [期限切れ] レポートを出す（期限 2026-04-01）
$ python todo.py add "テスト" --due 2026/11/1; echo $?
usage: todo.py add [-h] [--due DUE] title
todo.py add: error: argument --due: 期限は YYYY-MM-DD の形で指定してください: 2026/11/1
2
```

- `today` を引数で渡すのは、第8回で日付を固定してテストするため。`is_overdue` の中で `date.today()` を呼んでいても今回は正解にする（第8回の題材になる）
- コミットは main に3つ（`.gitignore`・版の固定・CLI）と、PR のブランチに1つ以上。`tasks.json` と `.venv` がコミットされていないこと

### PR の本文の例

```markdown
## 目的

締め切りのあるタスクを見落とさないように、期限を付けて期限切れだけを表示できるようにする。

Closes #1

## 変更点

- `add --due YYYY-MM-DD` で期限を保存する（JSON では文字列、なしは null）
- `list --overdue` で、未完了で期限が今日より前のものだけを表示する
- 一覧の状態に「期限切れ」を足す

## 確認方法

1. `python todo.py add "レポートを出す" --due 2026-04-01` → `[期限切れ]` で追加される
2. `python todo.py list --overdue` → 期限切れの1件だけが出る
3. `python todo.py add "テスト" --due 2026/11/1` → 形の誤りの文言と終了コード 2
4. 期限を足す前の `tasks.json` でも `python todo.py list` が動く
```

### 講師が見せる補足（任意）

時間が余ったときに講師の画面で見せます。受講者の課題にはしません。

- EAFP と LBYL: `load_tasks` を `if path.exists():` で書き直して比べる。確かめてから開くまでの間に消える場合を扱えない。壊れた JSON はどちらの書き方でも `except json.JSONDecodeError:` が要る。利用者に「`tasks.json` が壊れています」と出して終了コード 1 にするのがよい（黙って空にすると、次の保存でデータが消える）
- ジェネレータ: `def overdue(tasks, today):` を `yield` で書き、`list()` を2回呼ぶと2回目は空になることを見せる。`max((t["id"] for t in tasks), default=0)` の丸括弧もジェネレータ式
- `match` で `sys.argv[1:]` を直接振り分ける版: `case ["add", title]:`、`case ["done", task_id] if task_id.isdigit():`。短く書けるが、`--help` や `--due` の扱いを自分で書くことになる。argparse を使う理由の説明に使う

## 評価の観点

- 型ヒントが関数の引数と戻り値にあり、`except:` だけの書き方がないか
- データの操作（`add_task` など）と表示（`print`）が分かれているか
- 期限の当日を期限切れにしていないか、完了したタスクを期限切れにしていないか
- `tasks.json` と `.venv` を Git に入れていないか。期限の追加が PR（`Closes #1`）で入っているか
