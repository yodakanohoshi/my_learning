# 第11回 TDD による Web バックエンド（講師用）
tag: web-サーバ, db, test-自動
前提タグ: 設計-詳細, python-oop, test-自動, test-CI
所要: 座学15分 / ハンズオン45分

<!-- 講師用。受講者に配るときはこのファイルを除く -->

## 進行メモ

| 時刻 | 内容 | メモ |
| --- | --- | --- |
| 0:00 | 座学: 第10回の PR #14 の API設計書を見せる（3分） | 4章の入力チェックの表と 5章のシーケンス図を開き、「今日はこの文言とステータスコードをそのままテストに書く」と伝える。受け入れ条件 (1)〜(15) が今日のテストの元になる |
| 0:03 | 座学: 受講者用の「まとめ」を上から（12分） | 層と道具 → 依存性の注入 → TDD とテストの元 → アプリの形。依存性の注入は「テストのときだけ保存先と今日を差し替える」ことだけ伝え、仕組みは手順3の fixture を画面に出して説明する |
| 0:15 | ハンズオン 1 Issue とブランチ、依存パッケージ（4分） | `uv add` がプロキシで止まる人がいたら、第2・4回の設定を確かめさせる（つまずきやすい点）。Issue #15 のマイルストーンは `Web 版` |
| 0:19 | ハンズオン 2 SqliteStore（6分） | レッドは `ModuleNotFoundError`。`SqliteStore` はコピーして読む部品と位置づけ、`with self.conn:`・`?`・日付の変換の3点だけを画面で指す。`-v` の `[sqlite]` で「Protocol を満たした」ことを確かめる |
| 0:25 | ハンズオン 3 レッド: 追加のテスト（6分） | fixture の図を見せてから `test_1_…` を一緒に書く。「> 座学:」で **レッドの表示を全員で読む** 時間を必ず取り、「何がないから落ちたか」を言わせる |
| 0:31 | ハンズオン 4 グリーン: web.py とテンプレート（8分） | 素材の `web.py` をコピーした後の 404 も読ませる（URL がない）。`add_task` は講師の画面を写す。グリーンになった瞬間を全員で確かめる |
| 0:39 | ハンズオン 5 入力エラー（5分） | 422 と `InvalidTaskError` の2つの落ち方が今日の山場。「設計書は 400 と言っている」と突き合わせ、型の変換は FastAPI、決まりは `models.py` と分ける理由を話す |
| 0:44 | ハンズオン 6 完了と 404（5分） | (14) が「404 なのに落ちる」ことに注目させる。文言まで確かめるから、URL がないだけの 404 と区別できる |
| 0:49 | ハンズオン 7 残りのテスト（4分） | コピーしたテストは最初から通る。壊して落ちるのを2つ見せ、`| safe` は第3回の XSS につながると一言だけ |
| 0:53 | ハンズオン 8 ブラウザと curl（3分） | ブラウザで追加・完了・「期限切れだけ」を触らせる。curl は講師の画面だけでもよい。303・`Location`・`--data-urlencode` は第3回で済んでいるので説明しない |
| 0:56 | ハンズオン 9 PR とマージ（4分） | `Closes` を1行ずつ書くことを強調する。CI を待つ間に Commits タブでレッドとグリーンの順を見せる。時間が足りなければ push と PR の作成までにして、マージは CI が緑になってから各自で行う |

手順2・7はコピーが中心なので、押したら説明を短くします。手で書くテスト（手順3・5・6）と、レッドの表示を読む時間は削らないでください。手順8の curl は講師の画面だけにしてもゴールに影響しません。

第11回は振り返り・宿題・発展課題を設けません。手順9のマージまでで、第12回が前提にする main（`web.py`・`render_index`・`templates/`・`tests/test_web.py`）がそろいます。

### 事前に確認すること

- 受講者の `todo-app` が第10回の終わりの状態で、`mise run check` が通るか。遅れた人には [session-10/](../../examples/todo-app-snapshots/session-10/) をコピーして始めてよいと伝える
- 社内プロキシ越しに PyPI へ届くか（[open-questions.md](../open-questions.md) の Q1・Q3・Q5）。最初の手順が `uv add` なので、ここで止まると全体が止まる
- GitHub Actions が受講者のリポジトリで動くか（Q11）。第8回で緑になったことがあれば足りる
- ストーリーの Issue #8〜#11 とマイルストーン `Web 版` があるか（第9回の手順8）。GitLab では番号が違うので、出た番号で読み替えさせる
- ハンズオンの手順は、第10回の見本をコピーした状態から通して確かめておく（下の解答例は 2026-10-13 に通した結果）

## つまずきやすい点

| 症状 | 原因 | 対処 |
| --- | --- | --- |
| `uv add` が SSL エラーやタイムアウトで止まる | プロキシ・社内 CA の設定が uv に効いていない | 第2・4回の手順書の `https_proxy`・`SSL_CERT_FILE`（または `UV_NATIVE_TLS=1`）を確かめる |
| テストで `Using httpx with starlette.testclient is deprecated` の警告 | `httpx` を入れた | `uv remove --dev httpx; uv add --dev httpx2`。TestClient の書き方は変わらない |
| `cp …/{.gitignore,mise.toml} .` で `No such file` | `{}` の中にスペースを入れた、または bash 以外のシェル | `{.gitignore,mise.toml}` をスペースなしで書く。だめなら2回に分けて `cp` する |
| 手順4の後も `ModuleNotFoundError: No module named 'todo.web'` | `web.py` を `src/todo/` ではなく直下やテストの下にコピーした | `ls src/todo` で確かめる |
| 手順4の後に `TemplateNotFound: index.html` | `templates` を `src/todo/` の下にコピーしていない | `ls src/todo/templates` で `base.html`・`index.html` を確かめる |
| `git add .` でテストと実装が1コミットに混ざる | ファイルを指定せずに add した | `git add tests/test_web.py`・`git add src` と分ける。混ざったら `git reset HEAD~` でやり直す |
| 手順4の後に `mise run lint` が F401（未使用の import） | 手順5・6の `InvalidTaskError`・`TaskNotFoundError` を先に import に足した | 使う手順で足す。`mise run fmt` で消えた場合は、使う手順で足し直す |
| 手順5の空のタイトルが 422 の JSON のまま | `title` に既定値 `= ""` を付けていない（`add_task` を置き換えていない） | 手順5のコードで `add_task` を丸ごと置き換える |
| 文言が設計書と違う／`"   "` が通る | 自分で `if not title:` などを書き直した | 第7回の `validate_title`・`parse_due` をそのまま呼ぶ。決まりと文言は CLI と1か所 |
| 手順6のテストで 303 のはずが 200 | `follow_redirects=False` を付けていない | TestClient は既定でリダイレクトを追う。付けた場合と付けない場合の違いを見せ、第3回のログインの 303 と結び付ける |
| `?overdue=yes` でも絞り込まれる | `overdue: bool` で受けた（Pydantic は `yes`・`true` も真にする） | API設計書は「`1` のときだけ」。素材のとおり `overdue: str = ""` で受けて `== "1"` で比べる |
| テストを2回流すと件数が増える／順番で落ちる | 開発用の `var/todo.db` を使っている。`dependency_overrides` の差し替えが効いていない | fixture で `get_store` を `tmp_path` の DB に差し替え、`yield` の後で `clear()` |
| `sqlite3.ProgrammingError: ... thread` | 接続を作ったスレッドと使うスレッドが違う（FastAPI は同期の関数を別スレッドで動かす） | 見本の `SqliteStore.open` は `check_same_thread=False`。接続はリクエストごとに `get_store` で開いて閉じる |
| curl で追加したタイトルが `ç‰›ä¹³` のように化ける | `-d "title=牛乳を買う"` で送った（エンコードしていない） | `--data-urlencode` を使う。ブラウザのフォームは自動でエンコードする |
| `127.0.0.1:8000` が開けない | `NO_PROXY` に localhost が入っていない、または前の `mise run dev` が残っている | 第2回の手順書で `NO_PROXY`・`no_proxy` を確かめる。`ss -tlnp \| grep 8000` で残ったプロセスを探して止める |
| マージしても #9〜#11 が閉じない | `Closes #8, #9` のように番号だけを並べた／全角の `＃` | Issue ごとに `Closes #番号` を書く。閉じなかった Issue は手で閉じ、PR へのリンクを残す |
| CI だけ失敗する | `uv.lock` や `templates/` のコミット漏れ | CI のログの失敗した行を読み、`git status` で漏れを探す |

## 解答例

模範は [`examples/todo-app-snapshots/session-11/`](../../examples/todo-app-snapshots/session-11/)（フォルダ単体で `mise run setup && mise run check` が通る）。第10回の見本と同じ状態から手順1〜9を通すと、`src/` と `tests/test_store.py` は模範と一致します。

### 受講者の手元との違い

| ファイル | 違い | 後の回への影響 |
| --- | --- | --- |
| `tests/test_web.py` | テストは同じ20件。手で書いた (1)・(3)・(13)・(14) が先、コピーした分が後に並ぶ | ない（第12回はこのファイルの末尾にテストを足す） |
| `pyproject.toml` | 依存の下限（`"httpx2>=2.13.1"` など）と表の位置。`python-multipart` などのコメントがない | ない |
| `tests/test_models.py`・`test_sort.py`・`cli.py` | 第8回からの違いのまま | ない |

### 手順ごとの結果

| 手順 | コマンド | 結果 |
| --- | --- | --- |
| 1 | `mise run check` | 28 passed |
| 2 レッド | `mise run test` | `ModuleNotFoundError: No module named 'todo.sqlite_store'` |
| 2 グリーン | `uv run pytest -v tests/test_store.py` | 15 passed（`[sqlite]` が4件と開き直しのテスト）。全体は 33 passed |
| 3 | `mise run test` | `ModuleNotFoundError: No module named 'todo.web'` |
| 4 コピー後 | `mise run test` | `assert 404 == 200`（`POST /tasks` がない） |
| 4 グリーン | `mise run check` | 34 passed |
| 5 レッド | `mise run test` | `[]` は `assert 422 == 400`、`[   ]` は `todo.models.InvalidTaskError: タイトルを入力してください` |
| 5 グリーン | `mise run check` | 36 passed |
| 6 レッド | `mise run test` | (13) は `assert 404 == 303`、(14) は本文が `{"detail":"Not Found"}` |
| 6 グリーン | `mise run check` | 38 passed |
| 7 | `mise run test` | 53 passed。並べ替えを外すと `test_7_…` だけ、`\| safe` で `test_10_…` だけが落ちる |
| 9 | `git log --oneline main..` | 11コミット（依存パッケージ → レッド／グリーン×4 → テスト → README） |

手順2で DB の中身を表示した結果です（`created_at` は実行した時刻）。

```text
Task(id=1, title='牛乳を買う', due=datetime.date(2026, 11, 1), done=False)
[(1, '牛乳を買う', '2026-11-01', 0, '2026-10-13T02:28:58')]
```

### 説明どころ

- `with self.conn:` はコミット・ロールバックだけで、接続は閉じない。閉じるのは `get_store` の `finally` の `close()`
- `check_same_thread=False` は、FastAPI が同期の依存関係とルートを別々のスレッドで動かすため。1リクエストで1接続なので、同時には使わない
- 手順5の 422 は、FastAPI が `Form()` の必須の値が空だと関数を呼ぶ前に返すもの。`/tasks/abc/done` が 422 になるのも同じ仕組み（`task_id: int` の変換）。設計書のステータスコードにしたいものは、既定値を付けて関数まで届け、自分で返す
- `render_index` は一覧・400・404 を1つで描く。第12回は、隣に一覧の断片だけを描く関数を足し、同じ `index.html` から一覧を切り出す

### PR の例

```markdown
## 目的

Web 版を、受け入れ条件のテストを先に書いて作る。

Closes #15
Closes #8
Closes #9
Closes #10
Closes #11

## 変更点

- `SqliteStore`（`TaskStore` の SQLite 版）。保存先のテストを3つの保存先で動かす
- `web.py`（`GET /`・`POST /tasks`・`POST /tasks/{id}/done`）とテンプレート
- `tests/test_web.py`（テスト名の頭に受け入れ条件の番号）。(1)・(3)・(13)・(14) はテストを先に書き、残りは見本からコピーして壊して確かめた
- 設計書は変えていない（API設計書 5章のシーケンス図どおり）

## 確認方法

1. `mise run check` が通る（53 passed）
2. `mise run dev` で http://127.0.0.1:8000/ を開き、追加・完了・「期限切れだけ」ができる
```

### 講師が見せる補足（任意）

時間が余ったとき、または質問が出たときに講師の画面で見せます。受講者の課題にはしません。

- Pydantic のフォームモデル: `class TaskForm(BaseModel)` に `field_validator("title", mode="before")` で `validate_title` を呼ぶ。`Annotated[TaskForm, Form()]` で受けると検証失敗が 422 の JSON になり、400 の画面にするには例外ハンドラが要る（だから本編では使わない）
- 境目のテストの足し方: 期限の当日と前日（`test_9_…`）、100文字と101文字（`test_4_…`）、完了済みをもう一度完了（`test_完了済みを…`、API設計書 6章）。コピーした分に入っているので、どれがどの境目かを読み合わせる
- `due` を TEXT にした理由: SQLite には日付型がなく、ISO 形式（`YYYY-MM-DD`）の文字列なら文字列の比較・並べ替えが日付の順と一致する（DB設計書）
- インデックス: 件数が増えたら `due` に索引を張る話（副読本『達人に学ぶDB設計徹底指南書』6章）。今は全件を読んで Python で並べている

## 評価の観点

- 履歴でレッド → グリーンの順が追えるか。テストと実装が別のコミットか（横断テーマ「TDD」）
- テストが受け入れ条件・API設計書と対応しているか（ステータスコードと文言、テスト名の番号）
- テストが開発用 DB に触れず、依存性の注入で差し替えているか
- CI が緑の状態でマージし、`Closes` で Issue #8〜#11・#15 が閉じているか

## カリキュラムとの関係（報告事項）

- 2026-10-13 の作り直しで、所要を座学15分 / ハンズオン45分にし、振り返り・宿題・発展課題をなくした。旧宿題（残りのストーリーをテスト先行で完成させ、CI を通して PR）はハンズオンに入れた。手で書くテストは追加・入力エラー・完了・404 に絞り、残りの受け入れ条件のテストは見本からコピーして読み、壊して確かめる形にした。第12回が模範の `web.py`・`templates/`・`tests/test_web.py` を前提にしているため
- ブランチは Issue #15（タスク）に対して切り、PR #16 で #15 とストーリーの #8〜#11 を閉じる（1 Issue = 1 ブランチの規約に合わせた）
- `SqliteStore` は手で書かず、見本をコピーして読む。代わりに第8回の保存先のテストに `"sqlite"` を足すレッドから入り、Protocol の差し替えをテストで確かめる
- TestClient が使う HTTP ライブラリは `httpx2`。Starlette 1.x は `httpx` だと非推奨の警告を出す（テストの書き方は同じ）
