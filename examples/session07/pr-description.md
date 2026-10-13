# リファクタリング PR の説明の見本

第7回の手順7の PR の例です。[PR テンプレート](../../docs/templates/pull_request.md) の項目で書いています。

---

**タイトル**: todo.py をパッケージに分け、ruff と mypy で確かめる

## 目的

1ファイルの `todo.py` は、タスクを dict で持っているため、キーの書き間違いが動かすまでわからない。保存先も JSON に決め打ちで、差し替えて試せない。一覧の表示は変えずに、読みやすく壊れにくい形にする。

Closes #3

## 変更点

- `todo.py` を `src/todo/cli.py` に移し、`uv run todo ...` で動くようにした（1つ目のコミットは移しただけ）
- タスクを `Task`（`frozen=True` の dataclass）、状態を `Status`（Enum）にした（`src/todo/models.py`）
- 保存先の約束を `TaskStore`（Protocol）にし、`JsonStore` と `MemoryStore` を用意した（`src/todo/store.py`）
- ruff（コーディング規約）と mypy（strict）の設定を `pyproject.toml` に、確かめるタスクを `mise.toml` に入れ、指摘をなくした
- README に開発環境・使い方・コードの構成・人が見るコーディング規約を書いた
- 変えたこと: エラーの文言を `models.py` の決まりにそろえた（例: 「タイトルを入力してください」）。`--due` の形の誤りは終了コード 2 から 1 になった
- 変えていないこと: コマンドの使い方、一覧の表示、`tasks.json` の形（第6回のファイルをそのまま読める）

## 確認方法

1. `mise run setup` のあと `mise run check` が通る
2. 第6回で作った `tasks.json` があるディレクトリで `uv run todo list` を実行し、第6回の `python todo.py list` と同じ表示になる
3. `uv run todo add "テスト" --due 2026/11/1` で「期限は YYYY-MM-DD の形で入力してください」と出て、終了コードが 1 になる（`echo $?`）

## セルフチェック

- [x] 目的と変更点が一致している（関係のない変更が入っていない）
- [x] コミットが「何を・なぜ」の単位に分かれていて、メッセージで説明できている
- [x] 確認方法の手順を自分で一度実行した
- [x] 秘密情報や `.venv`・`tasks.json`・`var/` などの不要なファイルが入っていない

---

## セルフレビューのコメントの例

PR の差分を他人のつもりで読み、行にコメントする。接頭辞は[研修の規約](../../docs/session05/assets/commit-convention.md)の7。

| 場所 | コメント |
| --- | --- |
| `cli.py` の `--due` の引数 | [確認] `type=parse_due` をやめ、`run_add` で `parse_due` を呼ぶ形にした。形の誤りの終了コードが 2 から 1 に変わるが、文言を `models.py` の1か所にそろえるため意図どおり。変更点に書いた |
| `store.py` の `JsonStore._from_json` | [確認] `item.get("due")` で読むので、第6回の `due` のキーがないタスクも読める。`uv run todo list` で確かめた |
| `store.py` の `JsonStore.mark_done` | [質問] 呼ぶたびにファイル全体を読み書きしている。件数が増えたら遅くならないか → 個人の TODO の件数なら問題ない。第11回で SQLite に差し替える |
| `models.py` の `Task.status` | [良い点] 期限切れの判定が1か所にあり、`cli.py` は `status(today).value` を表示するだけになった |

## この見本のポイント

- **目的** に、今の形の何が困るか（dict のキーの書き間違い、保存先の決め打ち）が書いてある
- **変更点** に「変えたこと」と「変えていないこと」を分けて書いてある。リファクタリングは動きを変えないことが前提なので、変えた所はレビュアーが真っ先に確かめる
- **確認方法** で、前と同じ表示になることを第6回の `tasks.json` で確かめている
