# スクリプト

| パス | 内容 |
| --- | --- |
| `scripts/` | 研修で動かすスクリプト（演習素材の生成、資料の検査、タグ索引の生成、配布物の作成） |
| `tests/` | `scripts/` のテスト |

依存パッケージは `pyproject.toml` と `uv.lock` で管理しています。Python は mise が入れたものを使い、システムの Python は使いません。

```sh
cd tools
mise trust && mise install   # Python 3.12 と uv
mise run setup               # uv.lock どおりに依存パッケージを入れる
```

## タスク

| タスク | 内容 |
| --- | --- |
| `mise run build` | 資料を直したらこれだけ叩く。`tag-index` → `check` → `diagrams` → `docs` を順に実行する（検査で指摘があればそこで止まる） |
| `mise run setup` | 依存パッケージを `uv.lock` どおりに入れる |
| `mise run check` | 全回の資料の冒頭形式（tag／前提タグ／所要）、タグ・所要とカリキュラムの一致（所要の合計が60分か）、見出しを検査する。`mise run check -- --strict` は「（作成中）」も指摘する |
| `mise run tag-index` | 資料の冒頭とカリキュラムから、`docs/tags.md` と `docs/tags/<タグ名>/README.md` を生成する |
| `mise run session01-logs` | 第1回の演習用ログ（`docs/session01/assets/logs/`）を再生成する。シード固定なので毎回同じものができる |
| `mise run test` | `scripts/` の ruff・mypy・pytest |
| `mise run diagrams` | カリキュラムと各回の資料の冒頭から、知識の系統図（`knowledge-map`）と研修の全体像の図（`overview`）を `docs/diagrams/` に生成する。HTML 版は Playwright の Chromium で PNG・PDF に、Mermaid 版（block-beta）は mermaid-cli で PNG にする。新しい環境では最初に一度 `mise exec -- playwright install chromium` を実行する |
| `mise run docs` | `docs/` の Markdown（講師用を除く）を Vivliostyle で HTML 版と PDF 版にする。HTML 版は `docs/_build/html/index.html`（目次）から開き、コードブロックのコピーボタン、ページ下の「戻る」・目次・全体概要・タグ一覧のナビ付き。PDF 版は全部を1冊にした `docs/_build/handsoff.pdf` で、資料どうしのリンクはページジャンプ、各ページの下に目次・全体概要・タグ一覧へのリンク（「戻る」は PDF ビューアの機能を使う）。見た目は `docs_theme/`。Mermaid と PlantUML のコードブロックは図（SVG）にして埋め込む（PlantUML には Java が要る。`mise install` で入り、PlantUML の jar は初回に `.cache/` へ取ってくる） |
| `mise run docs -- --no-pdf` | HTML 版だけを作り直す（PDF は作らないので速い）。資料を直しながらブラウザで見た目を確かめるとき用 |
| `mise run docs-serve` | HTML 版をスマホやタブレットから見られるように配信する。同じ Wi-Fi で開く URL と QR コードを表示する（既定のポートは 8765。`-- --port 番号` で変える）。WSL では mirrored モードが要り、開けないときは表示される PowerShell のコマンドで Windows のファイアウォールを許可する |
| `mise run dist -- <出力先>` | 受講者に配る一式を作る。研修ディレクトリをコピーし、`.git`・仮想環境とキャッシュ・`instructor.md`・`handoff.md`・`docs/_template/`・`.claude/` を除く。見本の TODO アプリ（`examples/todo-app/`・`examples/todo-app-snapshots/`）は git を使わないフォルダなのでそのまま入る。HTML 版・PDF 版（`docs/_build/`）も入れるので、先に `mise run docs` を実行しておく。出力先は研修ディレクトリの外の、空か存在しないディレクトリ |
