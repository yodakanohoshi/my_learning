# 第3回 Web 通信の基礎（HTTP・Cookie・Web API）（講師用）
tag: http, web-ブラウザ, sec
前提タグ: linux-シェル, linux-ネットワーク
所要: 座学15分 / ハンズオン45分

<!-- 講師用。受講者に配るときはこのファイルを除く -->

## 進行メモ

| 時刻 | 内容 | メモ |
| --- | --- | --- |
| 0:00 | 座学: 第1回の `curl -v` と第2回の切り分けの振り返し（2分） | 「第2回までは届くかどうか、今日は届いた後に何をやり取りしているか」と位置づける。HTTP は文字の行のやり取りで、ヘッダは「名前: 値」の約束事だと確かめる |
| 0:02 | 座学: 受講者用の「まとめ」を上から（13分） | 主なヘッダ → ステータスコード → Cookie とセキュリティ → Web API → 開発者ツール。セキュリティの表は「手順3・4・6・7で全部動かす」と予告するだけにして、用語の説明は短くする |
| 0:15 | ハンズオン 1 デモのサーバとヘッダ（7分） | ターミナル①でデモを起動させ、以降は止めない。`curl -v` の注釈を指でたどらせる。`Date` が世界標準時であること、`Content-Length` と実際の本文の長さが一致することに触れる |
| 0:22 | ハンズオン 2 Network タブ（5分） | 「ログを保持」に✓を入れてから再読み込み。304 は2回目の再読み込みで出る（初回は 200）。`/headers` は curl との違い（`Accept`・`Sec-Fetch-*`・`Cookie`）を言わせる |
| 0:27 | ハンズオン 3 Cookie とセッション（9分） | 山場の1つ。`visits=999` で「Cookie は書き換えられる → だから ID だけ渡して中身はサーバ」を全員に言わせる。古い ID で 401 になるのを見せ、ログアウトはサーバ側を消す操作だと押さえる |
| 0:36 | ハンズオン 4 CSRF（5分） | 2つの罠の URL の違い（403 と 401）を、オリジンとサイトの表で説明する。「Cookie は自動で付くから、本人が押したかはトークンで確かめる」 |
| 0:41 | ハンズオン 5 Web API と JSON（11分） | もう1つの山場。`jq` が入らない人は `python3 -m json.tool --no-ensure-ascii` で進める。わざと失敗させる5行は、コードと `detail` を声に出して読ませる。公開 API が社内で通らないときは講師の画面で見せ、受講者はデモで代える |
| 0:52 | ハンズオン 6 CORS とプロキシ（4分） | コンソールの CORS エラーと、ターミナル①の `Origin: http://localhost:8001` のログを並べて見せる。「CORS はブラウザが読ませないだけで、リクエストは届く」 |
| 0:56 | ハンズオン 7 DOM・fetch・XSS（4分） | `innerHTML` と `/search-unsafe` でダイアログが出るのを全員で見る。ダイアログに `session_id` が出ないことを手順3の `HttpOnly` と結び付ける。最後にデモのサーバを止めさせる |

押したら、手順5の「更新して消す」と「変わっていなければ 304」、手順7の「fetch で追加して DOM に足す」を講師の画面だけにします。手順3の Cookie の書き換えと古い ID の 401、手順4の 403 と 401、手順5のわざと失敗させる5行、手順6のサーバのログは削らないでください。

第3回は振り返り・宿題・発展課題を設けません。成果物もありません。受講者の手元には `workspace/session03/` の `cookie.txt` などが残るだけです。

### 事前に確認すること

- 受講者の PC の `python3` で `web_demo.py` が起動するか（Ubuntu 24.04 の Python 3.12 で確かめてある。mise・uv は第4回なので使わない）
- Windows のブラウザから `http://127.0.0.1:8000` と `http://localhost:8001` の両方が開けるか（WSL の localhost の転送）。社内では Windows のプロキシ設定の例外に `127.0.0.1;localhost` が要る（[open-questions.md](../open-questions.md) の Q1）
- 受講者のブラウザが Chrome か Edge か（資料の画面の名前はこの2つの日本語表示に合わせている）
- `https://jsonplaceholder.typicode.com` が社内のプロキシで通るか。通らなければ手順5の最後は講師の画面で見せる
- `sudo apt install jq` が通るか（第2回の apt のプロキシ設定）

### デモのサーバの作り

[assets/web_demo.py](assets/web_demo.py)（標準ライブラリだけ、ruff と `mypy --strict` を通してある）。

| URL | 中身 | 使う手順 |
| --- | --- | --- |
| `GET /` | トップ。Cookie `visits`（`HttpOnly` なし）を数え、ログインのフォーム、ピン留め（CSRF トークンつき）、タスクの一覧 | 1〜4・7 |
| `GET /static/style.css` | `ETag` と `Cache-Control: no-cache`。`If-None-Match` が一致すれば 304 | 2 |
| `GET /headers` | 受け取ったリクエストヘッダを JSON で返す | 1・2 |
| `POST /login`・`POST /logout` | セッションを作る・消す（`session_id` に `HttpOnly; SameSite=Lax; Max-Age=1800`） | 3 |
| `POST /pin` | セッションなしは 401、トークン違いは 403、成功は 303 | 4 |
| `GET /api/me` | ログイン中の利用者。CORS の許可なし | 3・6 |
| `/api/tasks`・`/api/tasks/{id}` | タスクの Web API（GET・POST・PATCH・DELETE・OPTIONS）。`localhost:8001` のオリジンにだけ CORS を許可 | 5・6・7 |
| `GET /search`・`GET /search-unsafe` | 検索語をエスケープする・しない（XSS の体験用） | 7 |
| 8001 の `/`・`/trap` | 別のサイト。`/trap` は 8000 の `/pin` へ送るフォーム（トークンなし） | 4・6 |

- ログは1リクエスト1行で、`Origin` と `Cookie` の有無を出す（手順4・6で「届いている」ことを見せるため）
- データはメモリだけ。最初のタスクは「牛乳を買う」（未完了）と「本を返す」（完了）。起動し直すと元に戻り、id も 3 から振り直す

## つまずきやすい点

| 症状 | 原因 | 対処 |
| --- | --- | --- |
| `OSError: [Errno 98] Address already in use` | 8000・8001 番に前のデモや第1回の `http.server` が残っている | `ss -ltnp \| grep -E '800[01]'` で PID を見て `kill`。またはデモを `--port 8100 --other-port 8101` で起動し、URL を読み替える |
| ブラウザで開けない・社内のエラーページになる | Windows のプロキシ設定の例外に `127.0.0.1`・`localhost` がない | Windows の「プロキシ設定」の例外に `127.0.0.1;localhost` を足す |
| `localhost:8001` だけ開けない | WSL の localhost の転送が IPv6 で失敗している | `127.0.0.1:8001` は開けるか確かめる。手順4の「別のサイト」は講師の画面で見せる |
| Network タブに何も出ない・すぐ消える | 開発者ツールを開く前に読み込んだ／ページの移動で記録が消えた | 開いてから再読み込みする。「ログを保持」に✓ |
| 2回目の再読み込みでも 304 が出ない | 「キャッシュを無効化」に✓が入っている | ✓を外して再読み込み |
| curl のログインで `利用者を選んでください`（400） | `-d user=利用者01` を `--data-urlencode` にしていない／利用者名の打ち間違い | 資料のコマンドを貼り直す |
| `/api/me` が curl でずっと 401 | `-b cookie.txt` を付けていない／ログアウトした後の `cookie.txt` を使った | もう一度ログインのコマンドを打つ |
| 手順4の罠で 401 にも 403 にもならず 303 | ログインしたタブのトークンを手で付けて送った／トップのフォームで押した | `127.0.0.1:8001/trap` と `localhost:8001/trap` のアドレス欄を確かめる |
| 手順4で両方とも 401 | ブラウザでログインしていない（手順3のブラウザのステップを飛ばした） | `http://127.0.0.1:8000/` でログインし直す |
| JSON を送ると 415 | `-H 'Content-Type: application/json'` を付け忘れた | 付ける。415 は「わざと失敗させる」で見るものと同じ |
| `jq: command not found` | apt で入れていない・入れられなかった | `python3 -m json.tool --no-ensure-ascii` で整形する。取り出しは講師の画面で見せる |
| 公開 API がタイムアウト（28）・証明書のエラー（60） | プロキシ・社内 CA の設定（第2回） | `env \| grep -i _proxy` を確かめる。直らなければデモで代える |
| コンソールに貼れない（貼り付けの警告が出る） | Chrome が初めての貼り付けを止めている | 警告の指示どおりの文字（`allow pasting` など）を打ってから貼る |
| 手順6の fetch が CORS エラーにならない | 8000 番のページのコンソールで打った（同じオリジン） | アドレス欄が `localhost:8001` のタブで打つ |
| `/search-unsafe` でダイアログが出ない | アドレス欄で検索語が別の検索エンジンに送られた／`q=` を付け忘れた | URL 全体を貼る。Network で `search-unsafe?q=…` の行を確かめる |

## 解答例

受講者の環境（Ubuntu 24.04、Python 3.12、curl 8.5.0、Chrome）を想定した結果です。2026-10-13 に curl とヘッドレスの Chromium（Playwright）で確かめました。セッション ID・`ETag`・`Date` の値は人によって違います。

### 手順ごとの結果

| 手順 | コマンド・操作 | 結果 |
| --- | --- | --- |
| 1 | `curl -v -o /dev/null …/` | `200 OK`、`Set-Cookie: visits=1; Path=/; Max-Age=86400; SameSite=Lax`、`Content-Type: text/html; charset=utf-8` |
| 1 | `/headers` に `-H` | `Accept-Language`・`X-Hello` が JSON に足される |
| 2 | 再読み込みを2回 | 2回目に `style.css` が 304。要求に `If-None-Match`、応答に同じ `ETag` |
| 2 | ブラウザで `/headers` | `Accept: text/html,…`、`Sec-Fetch-Mode: navigate`、`Cookie: visits=…` |
| 3 | `-c`・`-b` で2回 | `visits` が 1 → 2。`cookie.txt` に `127.0.0.1 … visits 2` |
| 3 | `-b 'visits=999'` | 「開いた回数: 1000」 |
| 3 | curl でログイン | `303 See Other`、`Location: /`、`Set-Cookie: session_id=…; HttpOnly; Path=/; SameSite=Lax; Max-Age=1800`。`cookie.txt` の行頭に `#HttpOnly_` |
| 3 | `/api/me` | Cookie ありで `"user": "利用者01"`、なしで 401 `"ログインしていません"` |
| 3 | ログアウト後に古い ID | 401 |
| 3 | `document.cookie` | `'visits=…'` だけ |
| 4 | ピン留め | 「ピン留めしたタスク: 牛乳を買う」 |
| 4 | `127.0.0.1:8001/trap` | `POST /pin` 403「CSRF トークンが正しくありません」。要求に Cookie が付いている |
| 4 | `localhost:8001/trap` | `POST /pin` 401「ログインしていません」。要求に Cookie がない |
| 5 | 一覧 | 200、`ETag: "2e134b7fa0269f9d"`（起動直後の2件のとき）、`Cache-Control: no-cache`、`Content-Type: application/json` |
| 5 | `?done=false` と `jq` | `牛乳を買う` |
| 5 | 追加 | `201 Created`、`Location: /api/tasks/3` |
| 5 | PATCH・DELETE・GET | 200（`"done": true`）・204・404 |
| 5 | わざと失敗 | 415・400・422・405（`Allow: GET, POST`）・404 |
| 5 | `If-None-Match` | 304。追加後は 200 と新しい `ETag` |
| 5 | JSONPlaceholder | `/todos/1` は 200、`cache-control: max-age=43200`。絞り込みは 9 件。POST は 201 と `location: …/todos/201`、その URL の GET は 404 |
| 6 | 8001 から `/api/me` | コンソールに CORS エラー、`TypeError: Failed to fetch`。ターミナル①に `"GET /api/me HTTP/1.1" 401  Origin: http://localhost:8001  Cookie: なし` |
| 6 | 8001 から `/api/tasks` | 配列が返る。応答に `Access-Control-Allow-Origin: http://localhost:8001` |
| 6 | curl で `/api/me` | 401 の JSON が読める |
| 7 | `textContent`・`innerHTML` | 前者は文字のまま、後者はダイアログ `1` |
| 7 | `/search-unsafe` | ダイアログに `visits=…` だけ。`/search` は見出しに文字のまま |

### 説明どころ

- Cookie の値は利用者の手元にあり、書き換えられる。セッションは「中身をサーバに置き、ID だけを渡す」ことで、書き換えても他人になりすませないようにしている（ID は推測できない乱数）
- ログアウトでサーバ側を消さないと、盗まれた ID が期限まで使える。デモはサーバ側でも30分の期限を持つ
- CSRF の守りは2段。`SameSite=Lax` は別のサイトからの POST に Cookie を付けない（ブラウザの守り）。トークンは同じサイトの中からでも、本人のフォーム以外を弾く（サーバの守り）。サイトはポートを見ないので、`127.0.0.1:8001` は同じサイト
- CORS はブラウザが読み取りを止めるだけ。リクエストはサーバに届いて処理される。サーバの変更を防ぐのは CSRF のトークン。curl には CORS がない
- `/api/tasks` は 415 → 400 → 422 の順に確かめる。形が読めないのが 400、読めたが中身がだめなのが 422。第11回の FastAPI も、入力の検証に通らないと 422 を返す
- 第12回で TODO アプリの画面を fetch で部分更新するとき、今日の DOM・fetch・`textContent` と `innerHTML` の違いを前提にする

### 講師が見せる補足（任意）

時間が余ったとき、または質問が出たときに講師の画面で見せます。受講者の課題にはしません。

- プリフライト: `localhost:8001` のコンソールで JSON を POST すると、先に `OPTIONS /api/tasks` が飛ぶ（ターミナル①のログに2行）。デモは `Access-Control-Allow-Methods: GET, POST` と `Access-Control-Allow-Headers: Content-Type` を返すので本体も送られ、201 が返る

    ```js
    await fetch("http://127.0.0.1:8000/api/tasks", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({title: "別のサイトから"})}).then(r => r.status)
    ```

- 別のオリジンから見えるヘッダ: 上の fetch で `r.headers.get("location")` は `null`。CORS では `Access-Control-Expose-Headers` で許可したヘッダしか JavaScript に見せない
- GitHub の API: `curl -si https://api.github.com/repos/git/git` で `x-ratelimit-remaining`（残りの回数）と `etag` を見せる。認証なしは IP ごとに1時間60回で、社内では全員が同じプロキシの IP になるので、受講者には打たせない。`If-None-Match` の 304 は回数に数えない
- `Secure` と https: 本番では `Secure` を付けて https だけで送る。デモは http なので付けていない

## 評価の観点

- ヘッダを「名前: 値」で読み、`Location`・`Set-Cookie`・`ETag` などの役割を自分の言葉で言えるか
- Cookie とセッションの違い（どこに何があるか）、`HttpOnly`・`SameSite`・トークンが何を防ぐかを区別できるか
- 失敗のステータスコード（400・404・405・415・422）を、送ったものと結び付けて説明できるか
- CORS と CSRF で「誰が何を止めるか」（ブラウザが読ませない／サーバがトークンで弾く）を区別できるか

## カリキュラムとの関係（報告事項）

- 2026-10-13 の回の構成の変更で新設した回。旧第11回「Webの基礎と素の JavaScript」のうちアプリに依存しない部分（Network タブ、Cookie とセッション・CSRF、CORS とプロキシ、DOM と fetch をコンソールで触る、XSS）を移し、HTTP のヘッダ・Cookie とセッション・Web API と JSON を厚くした
- 受講者はまだ mise・uv・アプリのリポジトリを持たないので、素材は標準ライブラリだけのデモのサーバ（`web_demo.py`）にした。旧第11回の `cookie_demo.py`（FastAPI）を元に、Web API・ETag・CORS・XSS のページと別のサイト（8001）を足した
- 罠のページを `127.0.0.1:8001` と `localhost:8001` の2つの URL で開けるようにし、トークン（403）と `SameSite`（401）の2段の守りを両方見せる形にした
- 公開 API は JSONPlaceholder にした（認証なし・回数の制限が実質ない・`/todos` が題材に合う）。GitHub の API は回数の制限があるので講師の補足に回した
