# 第7回 読みやすく壊れにくい Python（講師用）
tag: python-oop, python-可読性, test-静的解析, 標準
前提タグ: python-構文, env-python, git-github
所要: 座学15分 / ハンズオン45分

<!-- 講師用。受講者に配るときはこのファイルを除く -->

## 進行メモ

各自が「Issue #3 → ブランチ → `todo.py` をパッケージに移す → models・store・cli に分ける → ruff・mypy を入れる → README → PR → マージ」までを通します。第8回は `src/todo/` と `mise run check` が main にある状態から始めるので、手順5のコミットまでは全員が終えることを優先します。

| 時刻 | 内容 | メモ |
| --- | --- | --- |
| 0:00 | 座学: まとめ（15分） | 「第6回 → 第7回」（5分）は第6回の `todo.py` と見本の `src/todo/` を左右に並べて見せる。「用語と考え方」（4分）のダックタイピングは「`len()` は `list` でも `str` でも呼べる」から入り、`Protocol` は「その約束を mypy が確かめられる形にしたもの」と話す。「パッケージの形」（2分）は「知らないこと」の列を強調する。「規約の置き場所」「判断の基準」（4分）は、機械に任せる規約と人が見る規約の分け方を話す |
| 0:15 | ハンズオン 1 パッケージに移す（7分） | `git mv` で移すと、`todo.py` のままでは `todo` パッケージが読めない問題も避けられる（つまずきやすい点）。`uv run todo list` が第6回と同じ一覧を出したら、移しただけでコミットさせる |
| 0:22 | ハンズオン 2 models.py（8分） | 講師の画面で一緒に書く。`FrozenInstanceError` を全員に出させる。状態を保存せず `today` で決めることを、状態遷移の図で押さえる |
| 0:30 | ハンズオン 3 store.py（8分） | `JsonStore` の `_from_json` で、第6回の `due` のないタスクを読めることを指す。書き終えたら「> 座学:」で、`JsonStore` も `MemoryStore` も継承していないことを画面で指して2分 |
| 0:38 | ハンズオン 4 cli.py（6分） | 一覧が第6回と同じことと、エラーの文言と `--due` の終了コード（2 → 1）が変わったことを両方確かめさせる。変わったことは手順7の PR の変更点に書く |
| 0:44 | ハンズオン 5 ruff と mypy（9分） | 3つの実験（打ち間違い・名前の変更・未使用の import）は必ずやる。とくに名前の変更は、`list` は動くのに `done` で落ちることを見せ、Protocol と mypy が何を防ぐかを見せる。実験のあとは毎回 `git status --short` で元に戻ったことを確かめさせる |
| 0:53 | ハンズオン 6 README（3分） | コピーして「コーディング規約」の表を読むだけでよい。自分の決まりを足すのは任意 |
| 0:56 | ハンズオン 7 PR とマージ（4分） | 変更点は「変えたこと」と「変えていないこと」に分けて書かせる。時間がなければ `[確認]` のコメントを1件にしてマージまで進める |

時間が押したら、手順2の「入力チェックを確かめる」と手順3の「JsonStore の流れを追う」を講師の画面だけにします。手順7のマージが授業中に終わらなかった人は、第8回の前に済ませるよう伝えます（PR まで出してあれば、第8回の冒頭でマージしてから始められます）。

第7回は振り返り・宿題・発展課題を設けません。元の宿題は次のように扱いました。

| 元の宿題 | 扱い |
| --- | --- |
| 演習の PR を仕上げてマージ | 手順7に入れた |
| ruff の `select` に1行ずつ理由のコメント | 手順5で、理由のコメント付きの設定を書く |
| README（開発環境・使い方・コーディング規約） | 手順6で見本をコピーする（第6回では README を作っていないので新しく足す） |
| `cli.py` の読みにくい所を1つ直す（`リファクタ:` のコミット） | 外した。代わりに手順1〜6を「移す・作り直す・道具・文書」の4つのコミットに分け、移すだけのコミットで動きを変えないことを体験する |
| ルールを選び直す、`# noqa` で黙らせる | 「講師が見せる補足（任意）」へ |

元の発展課題（ABC と Protocol の比較、クラス図、`__post_init__` の案）は、クラス図をハンズオンの図に入れ、残りを「講師が見せる補足（任意）」に移しました。

### 事前に確認すること

- 社内プロキシ越しに PyPI へ届くか（[open-questions.md](../open-questions.md) の Q5）。手順5の `uv add --dev ruff mypy` が通らないと、手順5から先に進めない。手順1の `uv sync` は `uv_build` を取りに行くので、ここで先に止まることもある
- 受講者のリポジトリが第6回の終わりの状態（main に `todo.py`・`mise.toml`・`pyproject.toml`・`uv.lock`・`.gitignore`、PR #2 がマージ済み）か。遅れた人は [session-06/](../../examples/todo-app-snapshots/session-06/) をコピーして `git init` からやり直してよい
- 素材 `assets/`
    - `store.py`: 模範 [session-07/src/todo/store.py](../../examples/todo-app-snapshots/session-07/src/todo/store.py) から `TaskStore` と `MemoryStore` を抜き、「手順3」のコメントにしたもの。`TaskNotFoundError`・`_next_id`・`_mark_done_in`・`JsonStore`・変換の関数はそのまま
    - `cli.py`: 模範の `src/todo/cli.py` と同じ。`main(argv, store, today)` で「保存先」と「今日」を差し替えられる形にしてあり、第8回で `MemoryStore` と固定の日付でテストする
- 模範を変えたら、上の2つと資料のコード（手順2の `models.py`、手順3の2つ、手順5の設定）も作り直す。手順5・6は見本の `.gitignore` と `README.md` をコピーするので、見本を変えると受講者の手元も変わる
- GitHub では Issue と PR の番号が共通なので、Issue が #3、PR が #4 になる。GitLab では Merge Request は `!2` のように別の番号になるが、`Closes #3` で Issue は閉じる

### workspace の構成

```text
workspace/todo-app/       ← アプリのリポジトリ（第6回で作った）
├─ .gitignore              第6回の分＋.mypy_cache/・.ruff_cache/（手順5）
├─ README.md               見本のコピー（手順6）
├─ mise.toml               setup＋lint・fmt・typecheck・check（手順5）
├─ pyproject.toml, uv.lock package = false を消し、scripts・build-system・ruff・mypy（手順1・5）
├─ src/todo/
│  ├─ __init__.py
│  ├─ models.py            手順2で書く
│  ├─ store.py             素材＋手順3で書く
│  └─ cli.py               手順1で todo.py を移し、手順4で素材に置き換える
├─ tasks.json              第6回からのデータ。コミットしない
└─ .venv/・.mypy_cache/・.ruff_cache/   コミットしない
```

- 手順どおりに進めると、`src/todo/` と `.gitignore`・`mise.toml`・`README.md` は模範の `session-07/` と同じになる。`pyproject.toml` は `[dependency-groups]` の位置と `"mypy>=2.4.0"` のような下限の有無だけが違う（`uv add` が末尾に下限付きで書くため。どちらでもよい）
- main の履歴は第6回の4つ（`.gitignore`・版の固定・CLI・PR #2 のマージ）に、ブランチ `issue-3-package` の4つのコミットと PR #4 のマージコミットが足される

## つまずきやすい点

| 症状 | 原因 | 対処 |
| --- | --- | --- |
| `mise run setup` が `The lockfile at uv.lock needs to be updated` | `pyproject.toml` を変えたのに `--locked` で同期した | 正常。手順1のとおり `uv sync`（第4回の手順5と同じ） |
| `uv sync` が `Expected a Python module at: src/todo_app/__init__.py` | `[tool.uv.build-backend]` の `module-name = "todo"` がない（プロジェクト名 `todo-app` から `todo_app` を探す） | 手順1の `pyproject.toml` に置き換える |
| `uv run todo` が `Failed to spawn: todo` | `[tool.uv]` の `package = false` が残っていて、パッケージとして入っていない | `package = false` を消して `uv sync` |
| `uv run todo` で `ImportError: cannot import name 'main'` | `[project.scripts]` の書き間違い | `todo = "todo.cli:main"` |
| `No module named 'todo.models'; 'todo' is not a package` | `todo.py` を `git mv` せずにコピーし、リポジトリの直下に残っている（`python -c` は今のディレクトリの `todo.py` を先に見る） | `git rm todo.py`。手順1の `git mv` なら起きない |
| `NameError: name '_mark_done_in' is not defined` など | `store.py` の手順3の場所以外も消した・書き換えた | `assets/store.py` をコピーし直し、手順3の2か所だけに書く |
| 手順4の `uv run todo list` で `KeyError: 'title'` などが出る | `tasks.json` を手で編集して壊した | `tasks.json` を消してやり直してよい（コミットしていないデータ） |
| mypy が `Function is missing a return type annotation` | `strict = true` は戻り値の型ヒントも求める | `-> None` などを書く。`__init__` も `-> None` |
| mypy が `Missing type parameters for generic type "list"` | `list` だけで中身の型がない | `list[Task]`・`dict[str, Any]` のように書く |
| ruff の `I001`（import の順）や `E501`（行が長い） | 標準ライブラリ・外部・自分のパッケージの順でない／101文字以上 | `mise run fmt` で直る。`E501` は直らないので行を分ける |
| 手順5の `git restore` で元に戻らない | 手順4のコミットをしていない | `git status` で確かめ、`git diff` を見て手で戻してから手順4のコミットをする |
| `git status` に `.mypy_cache/` が出る | `.gitignore` をコピーしていない | 手順5の `cp` をやり直す |
| `uv add` で `Failed to fetch` | プロキシ・社内 CA | 第2回の手順書。`uv` は `HTTPS_PROXY` と `SSL_CERT_FILE` を読む |

## 解答例

模範は [examples/todo-app-snapshots/session-07/](../../examples/todo-app-snapshots/session-07/)、PR の本文とセルフレビューのコメントの見本は [examples/session07/pr-description.md](../../examples/session07/pr-description.md)。

### 手順1・4の実行例

第6回の手順5・7で4件を足し、1を完了にした `tasks.json` の例です。

```text
$ uv run todo list
  1 [完了] 牛乳を買う
  2 [未着手] 報告書を書く
  3 [期限切れ] レポートを出す（期限 2026-04-01）
  4 [未着手] 本を返す（期限 2030-03-31）
$ uv run todo --help
usage: todo [-h] {add,list,done} ...
$ uv run todo add "   "; echo $?
タイトルを入力してください
1
$ uv run todo add "テスト" --due 2026/11/1; echo $?
期限は YYYY-MM-DD の形で入力してください
1
$ uv run todo done 99; echo $?
タスクが見つかりません: 99
1
```

- 手順1（第6回のコードのまま）と手順4（作り直した後）で、`list` の表示は同じ。変わるのはエラーの文言（第6回は「タイトルは1〜100文字で指定してください」「期限は YYYY-MM-DD の形で指定してください: 2026/11/1」）と、`--due` の誤りの終了コード（2 → 1）
- 手順4以降に `add`・`done` をすると、`JsonStore` が全件を書き直すので、第6回の `due` のないタスクにも `"due": null` が付く。読み込みはどちらでも動く

### 手順2の実行例

```text
$ uv run python -c "from todo.models import Task; t = Task(id=1, title='牛乳を買う'); print(t); t.done = True"
Task(id=1, title='牛乳を買う', due=None, done=False)
Traceback (most recent call last):
  ...
dataclasses.FrozenInstanceError: cannot assign to field 'done'
```

### 手順5の実験の出力

```text
$ mise run typecheck        # task.titel
src/todo/cli.py:23: error: "Task" has no attribute "titel"; maybe "title"?  [attr-defined]

$ mise run typecheck        # JsonStore の mark_done を finish に
src/todo/cli.py:73: error: Incompatible types in assignment (expression has type "TaskStore | JsonStore", variable has type "TaskStore | None")  [assignment]
src/todo/cli.py:79: error: Argument 1 to "run_add" has incompatible type "TaskStore | None"; expected "TaskStore"  [arg-type]
（run_list・run_done も同じ）

$ mise run lint             # import os
I001 [*] Import block is un-sorted or un-formatted
F401 [*] `os` imported but unused
Found 2 errors.
[*] 2 fixable with `--fix`.
```

- 名前の変更の1行目は「`JsonStore` が `TaskStore` と認められず、`store` に入れられない」という意味。残りの行はその結果として出る。1行目から読むことを伝える

### コミットの例

```text
$ git log --oneline main..
142e161 README に開発環境・使い方・コーディング規約を書く
5093e56 ruff と mypy でコーディング規約と型を確かめる
3fa948e タスクを dataclass に、保存先を Protocol にする
9bf9df4 todo.py をパッケージ src/todo に移す
```

- `git show --stat HEAD~3` で、1つ目のコミットに `todo.py => src/todo/cli.py | 0` と出れば、中身を変えずに移しただけのコミットになっている

### 講師が見せる補足（任意）

時間が余ったときに講師の画面で見せます。受講者の課題にはしません。

| | `Protocol` | `abc.ABC` |
| --- | --- | --- |
| 実装する側 | 継承しない。メソッドの形が合えば mypy が認める | 継承が必要。抽象メソッドを実装しないとインスタンスを作れない |
| 確かめる時期 | mypy で（実行前） | 実行時（インスタンスを作るとき） |
| 向いている場面 | 自分で書き換えられないクラスや、テスト用の小さな代役を受け入れたいとき | 共通の処理を基底クラスにまとめたいとき |

- `__post_init__` でタイトルを確かめる案: 「不正な `Task` が作れない」利点があるが、`JsonStore` が保存済みのデータを読むときにも検査が走り、決まりを変えたときに古いデータが読めなくなる。模範は入力の入口（`cli.py` の `run_add`、第11回は `web.py`）で `validate_title`・`parse_due` を呼ぶ形にした
- ルールを選び直す: `uv run ruff check --select ALL --statistics .` で全ルールの指摘の数を見る。`D`（docstring）・`RUF001`（全角の記号）・`T201`（`print`）など、この研修のコードに合わないものが多いことを見せ、「全部入れるのではなく、理由を説明できるものを選ぶ」と話す
- 黙らせる例: 第8回でテスト名を日本語にすると `N802` が出る。`[tool.ruff.lint.per-file-ignores]` に `"tests/**" = ["N802"]` と理由のコメントを書く（第8回の手順1で入れる）

## 評価の観点

- `Task` が `frozen=True` で、状態の判定（期限切れ）が `Task.status` の1か所にまとまっているか
- `cli.py` が JSON の形を知らず、`TaskStore` だけに依存しているか
- `mise run check` が通り、ruff の設定に選んだ理由のコメントがあるか
- コミットが目的ごとに分かれ、PR の本文に「変えたこと」と「変えていないこと」、確認方法が書いてあるか。セルフレビューのコメントがあるか
