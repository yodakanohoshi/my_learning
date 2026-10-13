# タグ一覧

<!-- tools/scripts/build_tag_index.py で生成。手で編集しない -->

知識体系マップ（[curriculum.md](curriculum.md#知識体系マップ木構造)）のタグを並べたものです。
同じタグ名を、資料の冒頭と Issue ラベルで共通に使います。
タグ名のリンク先は、そのタグを扱う回と副読本をまとめた索引です。

| タグ | 内容 | 扱う回 |
| --- | --- | --- |
| [linux](tags/linux/README.md) | OS（Linux） | 1, 2 |
| [linux-ファイル](tags/linux-ファイル/README.md) | ファイルと権限：ファイル操作／パイプとリダイレクト／権限 | 1 |
| [linux-シェル](tags/linux-シェル/README.md) | シェル：環境変数とPATH／.bashrc／シェルスクリプト | 1, 2 |
| [linux-アプリ](tags/linux-アプリ/README.md) | パッケージとプロセス：apt／エディタ（nano／vim）／プロセス（ps・kill）／コンテナ（Docker） | 1, 2 |
| [linux-ネットワーク](tags/linux-ネットワーク/README.md) | 通信の基礎：ネットワーク層とアプリ層／TCP/IPとポート／DNS・hosts／curl・ss・ping | 1, 2 |
| [http](tags/http/README.md) | Web通信 | 3, 10 |
| [http-基本](tags/http-基本/README.md) | HTTPとは：アプリ層のプロトコル／リクエストとレスポンス／URI | 3 |
| [http-ブラウザ](tags/http-ブラウザ/README.md) | ブラウザの挙動：ページの読み込み／フォーム送信とリダイレクト／Cookie・セッション／CORS | 3 |
| [http-構成](tags/http-構成/README.md) | HTTPの構成：メソッド／ステータスコード／ヘッダ／キャッシュ | 3, 10 |
| [http-リアルタイム](tags/http-リアルタイム/README.md) | リアルタイム通信：ポーリング／SSE／WebSocket | 3 |
| [db](tags/db/README.md) | データベース：ER図・テーブル設計／SQL（SQLite） | 10, 11 |
| [sec](tags/sec/README.md) | セキュリティ：XSSとエスケープ／CSRF／秘密情報の管理 | 3 |
| [python](tags/python/README.md) | プログラミング（Python） | 6, 7 |
| [python-構文](tags/python-構文/README.md) | 言語機能：型ヒント／dict.get／内包表記／例外とwith／pathlib／パターンマッチ | 6 |
| [python-oop](tags/python-oop/README.md) | オブジェクト指向：ダックタイピング／Protocol／dataclass／ABC | 7 |
| [python-可読性](tags/python-可読性/README.md) | 読みやすいコード：命名／コメント／制御フロー／リファクタリング | 7 |
| [web](tags/web/README.md) | Webアプリケーション | 3, 11, 12 |
| [web-サーバ](tags/web-サーバ/README.md) | サーバ側：FastAPI／Jinja2テンプレート／Pydantic／依存性の注入 | 11 |
| [web-ブラウザ](tags/web-ブラウザ/README.md) | ブラウザ側：HTMLフォーム／fetch・DOM操作／DevTools／htmx | 3, 12 |
| [設計](tags/設計/README.md) | 設計 | 9, 10 |
| [設計-要件](tags/設計-要件/README.md) | 要件：ユーザーストーリー／受け入れ条件／非機能要件 | 9 |
| [設計-構成](tags/設計-構成/README.md) | システム構成：システム構成図 | 10 |
| [設計-詳細](tags/設計-詳細/README.md) | 詳細設計：API設計書／DB設計書 | 10 |
| [test](tags/test/README.md) | テストと品質 | 5, 7, 8, 11, 12 |
| [test-自動](tags/test-自動/README.md) | 自動テスト：pytest／TDD／テスト用DB | 8, 11 |
| [test-静的解析](tags/test-静的解析/README.md) | 静的解析：ruff／mypy／pyright | 7 |
| [test-CI](tags/test-CI/README.md) | CI：GitHub Actions／PR ごとの ruff・pytest の自動実行 | 8 |
| [test-レビュー](tags/test-レビュー/README.md) | レビューと不具合管理：コードレビュー／不具合票 | 5, 12 |
| [git](tags/git/README.md) | バージョン管理（Git） | 5 |
| [git-基礎](tags/git-基礎/README.md) | Gitの基本：commit／diff・log／.gitignore／revert | 5 |
| [git-github](tags/git-github/README.md) | GitHub での利用：ブランチ／PR・セルフレビュー／Issue／コンフリクト解決 | 5 |
| [env](tags/env/README.md) | 実行環境 | 4 |
| [env-mise](tags/env-mise/README.md) | ツールのバージョン管理：mise.toml／タスク | 4 |
| [env-python](tags/env-python/README.md) | Pythonの環境：uv／仮想環境／ロックファイル | 4 |
| [標準](tags/標準/README.md) | 開発標準：コーディング規約／ブランチ運用／コミット規約／レビュー基準 | 5, 7 |
| [pm](tags/pm/README.md) | プロジェクトマネジメント | 9 |
| [pm-見積](tags/pm-見積/README.md) | 計画と見積：タスクの分解／幅のある見積 | 9 |
| [pm-進捗](tags/pm-進捗/README.md) | タスク管理：Issue／ラベル・マイルストーン | 9 |
