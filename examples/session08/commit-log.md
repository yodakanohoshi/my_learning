# TDD のコミットの並びの見本

第8回のハンズオンを手順どおりに進めたときの `git log --oneline --reverse main..issue-5-sort` の例です。PR の「Commits」タブでも同じ順に見えます。

```console
$ git log --oneline --reverse main..issue-5-sort
8080021 テスト: 今の動作をテストで固定する
7f56583 PR ごとに mise run check を GitHub Actions で実行する
3573b2d レッド: 期限が近い順に並べるテスト
af4addf グリーン: 期限の順に並べる最小の実装
13c839f レッド: 期限なしは最後に並べるテスト
23828c9 グリーン: 期限なしを最後にする
c1b857a レッド: 期限が同じなら番号の順のテスト
8cb25a8 グリーン: 期限が同じなら番号の順にする
617c985 リファクタ: テストの番号の取り出しを ids にまとめる
5b1a686 レッド: list を期限が近い順に表示するテスト
0f49deb グリーン: list を期限が近い順に表示する
6a6d7f2 README にテストと CI を書く
```

| コミット | 手順 | テスト | 中身 |
| --- | --- | --- | --- |
| `8080021` テスト | 4 | 24件通る | 足す前に、今の動作（add・list・done・保存先）をテストで固定する |
| `7f56583` | 5 | 24件通る | CI を置く。ここで push し、Actions が緑になる |
| `3573b2d` レッド | 6 | 収集で失敗 | `test_期限が近い順に並べる` だけを足す。`sort_by_due` がないので `ImportError`。push して CI の赤も見る |
| `af4addf` グリーン | 6 | 25件通る | `sorted(tasks, key=lambda t: t.due)` だけ。mypy は期限なしの場合を指摘する |
| `13c839f`〜`8cb25a8` | 6 | 失敗 → 通る | テストを1つ足すたびに、通る最小の変更をする（期限なし → 同じ期限） |
| `617c985` リファクタ | 6 | 27件通る | テストの `[t.id for t in ...]` を `ids` にまとめる。動作は変えない |
| `5b1a686`・`0f49deb` | 7 | 失敗 → 28件通る | `uv run todo list` の表示を期限が近い順にする |
| `6a6d7f2` | 8 | 28件通る | README にテストと CI を書く |

## この見本のポイント

- テストのコミットと実装のコミットが分かれていて、レッドのコミットでは本当にテストが失敗している
- グリーンでは「テストが通る最小の変更」だけをする。整えるのはリファクタのコミットで、テストが通ったまま行う
- コミットメッセージの頭の `テスト:`・`レッド:`・`グリーン:`・`リファクタ:` で、PR の履歴だけで順序が追える
- 最終形は [`todo-app-snapshots/session-08/src/todo/models.py`](../todo-app-snapshots/session-08/src/todo/models.py) の `sort_by_due` と [`tests/test_sort.py`](../todo-app-snapshots/session-08/tests/test_sort.py)

## PR の本文の例

```markdown
## 目的

一覧で締め切りの近いタスクを先に見られるようにする。あわせて今の動作をテストで固定し、push のたびに CI で確かめる。

Closes #5

## 変更点

- pytest を入れ、`mise run check` にテストを足した（tests/ の4ファイル）
- `.github/workflows/check.yml` で push・PR ごとに `mise run check` を動かす
- `sort_by_due` を TDD で足し、`uv run todo list` を期限が近い順（期限なしは最後、同じ期限は番号の順）にした
- 変えていないこと: `list --overdue` で出るタスクと、`tasks.json` の形

## 確認方法

1. `mise run check` が通る（28 passed）
2. `uv run todo list` で期限の近いものが上、期限なしが下に出る
```
