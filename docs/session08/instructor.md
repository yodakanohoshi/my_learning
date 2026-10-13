# 第8回 テストと TDD（講師用）
tag: test-自動, test-CI
前提タグ: python-oop, test-静的解析, git-github
所要: 座学15分 / ハンズオン45分

<!-- 講師用。受講者に配るときはこのファイルを除く -->

## 進行メモ

各自が「Issue #5 → ブランチ → pytest を入れる → 今の動作をテストで固定 → CI を置いて push → `sort_by_due` を TDD で → `list` を TDD で → README → PR → CI が緑になってからマージ」までを通します。第9回以降はテストと CI が main にある状態から始めるので、手順5の push までは全員が終えることを優先します。

| 時刻 | 内容 | メモ |
| --- | --- | --- |
| 0:00 | 座学: まとめ（15分） | 「テストの種類」（2分）は、今日書くのは単体と結合で、E2E は第11回と伝える。「pytest の書き方」（3分）は名前だけ紹介し、手順2〜4で使う。「テストしやすい形」（3分）は、第7回で `main(argv, store, today)` にしておいた理由として話す。「TDD」（5分）は「先に失敗を見る」と「グリーンは一番簡単な実装でよい」を強調する。「CI」（2分）は「赤の PR はマージしない」だけを押さえる |
| 0:15 | ハンズオン 1 Issue・pytest（5分） | `pyproject.toml` と `mise.toml` の書き足しは講師の画面を見せながら。`no tests ran` で失敗するのを全員に見せる。`uv add` がプロキシで止まる人がいないか回る |
| 0:20 | ハンズオン 2 assert と parametrize（7分） | `<` を `<=` に変えて落とすところは必ず全員にやらせる。「> 座学:」で失敗の表示（`>` の行、`E` の行、組の名前 `[due2-False-Status.TODO]`）を画面で指して読む |
| 0:27 | ハンズオン 3 fixture と tmp_path（6分） | `-v` の `[memory]`・`[json]` を見せ、fixture は「引数名で受け取る」ことを押さえる。`tmp_path` の場所（`/tmp/pytest-of-<ユーザー名>/`）を `ls` で見せてもよい |
| 0:33 | ハンズオン 4 CLI を固定（5分） | `run` と `capsys` を読む。コミットの接頭辞が `テスト:` になる理由（動作は変えていない）を一言 |
| 0:38 | ハンズオン 5 CI（5分） | push したら待たずに手順6へ進ませる。Actions タブは手順6の途中で見る |
| 0:43 | ハンズオン 6 TDD で sort_by_due（10分） | レッドの `ImportError` を「何がないから落ちたか」で声に出して読ませる。最小の実装で通り、mypy だけが気づいているところを見せてから次のテストへ。Actions の赤は講師の画面で1つ見せれば十分。「> 座学:」で三角測量を1分 |
| 0:53 | ハンズオン 7 TDD で list（3分） | 手順6と同じ形。テストのファイルと実装のファイルを別々に `git add` していることを確かめる |
| 0:56 | ハンズオン 8 PR とマージ（4分） | Commits タブでレッドとグリーンが交互に並ぶのを見せる。チェックが緑になるまで1〜3分かかるので、その間にセルフレビュー |

時間が押したら、手順3の「保存先ごとに動くのを見る」と手順6の「mypy の指摘を見る」を講師の画面だけにします。手順8のマージが授業中に終わらなかった人は、第9回の前に済ませるよう伝えます（PR まで出してあれば、第9回の冒頭でマージしてから始められます）。

第8回は振り返り・宿題・発展課題を設けません。元の宿題は次のように扱いました。

| 元の宿題 | 扱い |
| --- | --- |
| `list` を期限が近い順に表示する（TDD） | 手順7に入れた（模範の `cli.py` は第8回からこの形なので、後の回の前提になる） |
| 今の動作のテストを足す（`add`、`done`、`JsonStore` が第6回の `tasks.json` を読める） | 素材 `test_cli.py`・`test_store.py` に入れ、手順3・4でコピーして読む。`parse_due` などは模範の `test_models.py` にある（下の解答例） |
| もう1機能を TDD で足し、別の PR にする | 外した。手順6・7で TDD のサイクルを4回通す。例（完了済みを `done` するとエラー、`list --today`）は「講師が見せる補足（任意）」へ |
| CI を設定し、緑になってからマージ | 手順5・8に入れた |

元の発展課題（カバレッジ、テスト名で仕様を読む、レッドのコミットを取り出す）は「講師が見せる補足（任意）」に移しました。

### 事前に確認すること

- 受講者のリポジトリが第7回の終わりの状態（main に `src/todo/`、`mise run check` が通る、PR #4 がマージ済み）か。遅れた人は [session-07/](../../examples/todo-app-snapshots/session-07/) をコピーしてよい
- GitHub Actions がアプリのリポジトリで使えるか（組織の設定で止められていないか、外部の Action `jdx/mise-action` が許可されているか。[open-questions.md](../open-questions.md) の Q11）。GitLab の場合は Runner が用意されているか（Q4）。使えない場合、手順5・8の CI は講師の画面で見せるだけにし、PR の前に手元で `mise run check` を流す運用にする
- 社内プロキシ越しに PyPI へ届くか（Q5）。手順1の `uv add --dev pytest` で止まると全体が止まる
- 素材 `assets/`
    - `test_store.py`: 模範 [session-08/tests/test_store.py](../../examples/todo-app-snapshots/session-08/tests/test_store.py) から `test_最初は空` を抜き、「手順3」のコメントにしたもの
    - `test_cli.py`: 模範の `tests/test_cli.py` から `test_doneでない番号なら終了コード1`（手順4）と `test_listは期限が近い順に表示する`（手順7）を抜き、コメントにしたもの。残りのテストは第7回の `cli.py` のままで通る
- 模範の名前（`list_all`・`main(argv, store=, today=)`・表示の形）を変えたら、上の2つと資料のコード（手順2・6・7）も作り直す
- GitHub では Issue と PR の番号が共通なので、Issue が #5、PR が #6 になる

### workspace の構成

```text
workspace/todo-app/       ← アプリのリポジトリ（第6回で作った）
├─ .github/workflows/check.yml   見本のコピー（手順5）
├─ .gitignore              第7回の分＋.pytest_cache/（手順1）
├─ README.md               見本のコピー（手順8）
├─ mise.toml               test を足し、check が lint・typecheck・test（手順1）
├─ pyproject.toml, uv.lock pytest、per-file-ignores、mypy の files、testpaths（手順1）
├─ src/todo/
│  ├─ models.py            sort_by_due（手順6）
│  ├─ store.py
│  └─ cli.py               run_list で sort_by_due（手順7）
├─ tests/
│  ├─ test_models.py       手順2で書く
│  ├─ test_store.py        素材＋手順3
│  ├─ test_cli.py          素材＋手順4・7
│  └─ test_sort.py         手順6で書く
└─ tasks.json・.venv/・各キャッシュ   コミットしない
```

- 手順どおりに進めると、`src/todo/models.py`・`.gitignore`・`README.md`・`.github/`・`tests/test_store.py`・`tests/test_cli.py` は模範の `session-08/` と同じになる
- 模範との違い（どちらでもよい）: `tests/test_models.py` は模範の11件のうち2件（模範には `mark_done`・タイトルの前後の空白と100文字・`parse_due` のテストもある）、`tests/test_sort.py` は模範の `test_元のリストは変えない` がない。`cli.py` の import は1行（模範は括弧で複数行。ruff はどちらも通す）。`pyproject.toml` と `mise.toml` は表の位置と下限（`"pytest>=9.1.1"`）だけが違う
- main の履歴は第7回までに、ブランチ `issue-5-sort` の12のコミットと PR #6 のマージコミットが足される

## つまずきやすい点

| 症状 | 原因 | 対処 |
| --- | --- | --- |
| `no tests ran`（終了コード 5） | テストがまだない／ファイル名か関数名が `test_` で始まらない | 手順1では正常。手順2以降なら名前を直す。`testpaths = ["tests"]` も確かめる |
| `ModuleNotFoundError: No module named 'todo'` | `.venv` に todo-app が入っていない | `uv sync`（`pyproject.toml` を変えた後なので `mise run setup` の `--locked` は止まる） |
| `fixture 'store' not found` | fixture を別のファイルに書いた、名前の打ち間違い | 同じファイルに書く。複数のファイルで使うなら `tests/conftest.py` に移す（ファイル名は固定） |
| ruff が `N802 Function name ... should be lowercase` | テスト名の日本語を命名規則（N）が指摘する | 手順1の `per-file-ignores` を書いたか |
| mypy が `Untyped decorator makes function ... untyped` | mypy が pytest を見つけられない（`.venv` に pytest がない） | `uv sync`。`which mypy` が `.venv/bin/mypy` か |
| mypy が `Function is missing a return type annotation`（tests） | `files` に `tests` を足したので、テスト関数にも `-> None` が要る | `-> None` を書く。fixture の引数にも型（`capsys: pytest.CaptureFixture[str]`） |
| テストを流すと手元の `tasks.json` が書き換わる | `main` に `store` を渡し忘れ、既定の `JsonStore(Path("tasks.json"))` が使われた | テストでは `run` を通す。既定の動作を確かめるテストは `monkeypatch.chdir(tmp_path)` で場所を移す（素材の最後のテスト） |
| レッドのはずが最初から通る | 前の手順で `sort_by_due` を書いてしまった／期待値が入力と同じ順 | テストの入力をわざと崩す。通ったら実装を壊して落ちるか確かめる |
| グリーン1の後に `mise run check` が失敗する | mypy が `t.due` の `None` を指摘している | 正常。グリーン1は `mise run test` だけでコミットし、グリーン2で消える |
| `git add -A` でテストと実装が1つのコミットに | ファイルを指定しなかった | `git add tests/test_sort.py` のように指定する。混ざったら `git reset HEAD~` で戻して分け直す |
| Actions が黄色のまま始まらない／`startup_failure` | リポジトリの Actions が無効、外部の Action が許可されていない | Settings → Actions を確かめる。許可されなければ講師に相談 |
| CI で `mise.toml` が信頼されていないと出る | `MISE_TRUSTED_CONFIG_PATHS` がない | 見本の `check.yml` をコピーし直す |
| CI だけ失敗する（手元では通る） | `uv.lock` や新しいファイルのコミット漏れ、`ruff format` していない | ログの失敗した行を読み、`git status` と手元の `mise run check` で再現する |

## 解答例

模範は [examples/todo-app-snapshots/session-08/](../../examples/todo-app-snapshots/session-08/)、コミットの並びの見本は [examples/session08/commit-log.md](../../examples/session08/commit-log.md)。

### 手順2の失敗の表示

```text
$ sed -i 's/self.due < today/self.due <= today/' src/todo/models.py; mise run test
>       assert task.status(TODAY) is expected
E       AssertionError: assert <Status.OVERDUE: '期限切れ'> is <Status.TODO: '未着手'>
E        +  where <Status.OVERDUE: '期限切れ'> = status(datetime.date(2026, 11, 1))
...
FAILED tests/test_models.py::test_状態は完了と期限と今日で決まる[due2-False-Status.TODO]
========================= 1 failed, 7 passed in 0.01s ==========================
```

- `due2` は「3番目の組（0から数える）の `due`」。`date` のように文字にしにくい値には、pytest が引数名と番号で名前を付ける

### 手順6・7のレッドの表示

```text
E   ImportError: cannot import name 'sort_by_due' from 'todo.models'
E       TypeError: '<' not supported between instances of 'datetime.date' and 'NoneType'
E       assert [3, 1, 4, 2] == [1, 3, 2, 4]
E         At index 0 diff: '  1 [未着手] レポートを出す（期限 2026-11-05）' != '  2 [期限切れ] 牛乳を買う（期限 2026-10-30）'
```

- グリーン1の後の `mise run typecheck`: `src/todo/models.py:43: error: Argument "key" to "sorted" has incompatible type "Callable[[Task], date | None]"; ...`（2件）。テストは通るが、期限なしのタスクで落ちることを、mypy はテストより先に指摘している

### コミットの例

```text
$ git log --oneline main..
6a6d7f2 README にテストと CI を書く
0f49deb グリーン: list を期限が近い順に表示する
5b1a686 レッド: list を期限が近い順に表示するテスト
617c985 リファクタ: テストの番号の取り出しを ids にまとめる
8cb25a8 グリーン: 期限が同じなら番号の順にする
c1b857a レッド: 期限が同じなら番号の順のテスト
23828c9 グリーン: 期限なしを最後にする
13c839f レッド: 期限なしは最後に並べるテスト
af4addf グリーン: 期限の順に並べる最小の実装
3573b2d レッド: 期限が近い順に並べるテスト
7f56583 PR ごとに mise run check を GitHub Actions で実行する
8080021 テスト: 今の動作をテストで固定する
```

- テストの数は、手順1で0件（失敗）→ 手順2で8 → 手順3で18 → 手順4で24 → 手順6で27 → 手順7で28

### sort_by_due の完成形

```python
def sort_by_due(tasks: list[Task]) -> list[Task]:
    """期限が近い順に並べる。期限なしは最後、期限が同じなら id の順。"""
    # タプルは前の要素から順に比べる: (期限なしか, 期限, id)。False < True なので期限ありが先
    return sorted(tasks, key=lambda t: (t.due is None, t.due or date.min, t.id))
```

- `t.due or date.min` の値そのものに意味はない（期限なしは先頭の要素で既に後ろに回っている）。`None` と `date` は比べられないので、比べられる値を置いている

### 講師が見せる補足（任意）

時間が余ったときに講師の画面で見せます。受講者の課題にはしません。

- レッドのコミットを取り出す: `git switch --detach 3573b2d; mise run test`（ImportError で落ちる）→ `git switch -`。PR の Commits タブでも、レッドのコミットに赤い印が付く（push したときだけ）
- カバレッジ: `uv add --dev pytest-cov` → `uv run pytest --cov=todo --cov-report=term-missing`。`if __name__ == "__main__":` の行などは通らない。100% を目標にせず、「通っていない行に、壊れたら困る判定があるか」で判断する
- テスト名で仕様を読む: `uv run pytest -v` の出力を上から読み、名前だけで何を確かめているか分かるか
- もう1機能を TDD で足す例
    - 完了済みを `done` するとエラー「すでに完了しています」: `MemoryStore` と `JsonStore` の両方に要る。手順3の `params` の fixture を使えば1つのテストで両方を確かめられる。共通の `_mark_done_in` で判定するとよい（模範には入っていない）
    - `list --today`: `Task.status` と同じく「今日」を引数で受け取って判定する。`date.today()` を関数の中で呼ぶと、テストで日付を固定できない

## 評価の観点

- 履歴で `テスト:` → `レッド:` → `グリーン:`（→ `リファクタ:`）の順が追えるか。テストと実装が別のコミットか（横断テーマ「TDD」）
- 境目（期限の当日、期限なし、同じ期限）がテストになっているか
- テストが手元のファイルや今日の日付に依存していないか（`MemoryStore`・`tmp_path`・固定の日付）
- CI が緑になってからマージしているか。赤のときにログを読んで自分で直せるか
