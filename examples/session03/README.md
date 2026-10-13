# 第3回 見本

[第3回の資料](../../docs/session03/README.md) のハンズオンで観察した結果の例です。第3回には成果物がないので、ここでは自分の画面と見比べるための表示を手順ごとに並べます。セッション ID・`ETag`・日時・ブラウザの版は人によって違います。

ハンズオンを終えてから見てください。受講者の作業場所は `workspace/session03/` です。

## 1. ヘッダの中身

```text
$ curl -s -H 'Accept-Language: ja' -H 'X-Hello: 1' http://127.0.0.1:8000/headers
{
  "method": "GET",
  "path": "/headers",
  "headers": {
    "Host": "127.0.0.1:8000",
    "User-Agent": "curl/8.5.0",
    "Accept": "*/*",
    "Accept-Language": "ja",
    "X-Hello": "1"
  }
}
```

## 2. Network タブ

| 名前 | ステータス | タイプ | 見どころ |
| --- | --- | --- | --- |
| `127.0.0.1` | 200 | document | 応答に `Cache-Control: no-store` と `Set-Cookie: visits=…` |
| `style.css` | 200 → 2回目の再読み込みで 304 | stylesheet | 応答の `ETag` と、要求の `If-None-Match` が同じ値 |

ブラウザで開いた `/headers` には、curl にないヘッダが並びます（Chrome の例。一部を省略）。

```text
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,...",
"Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
"Sec-Fetch-Site": "none",
"Sec-Fetch-Mode": "navigate",
"Sec-Fetch-Dest": "document",
"Accept-Encoding": "gzip, deflate, br, zstd",
"Cookie": "visits=3"
```

## 3. Cookie とセッション

```text
$ cat cookie.txt                  # ログインした直後
# Netscape HTTP Cookie File
#HttpOnly_127.0.0.1	FALSE	/	FALSE	1791853267	session_id	aRVPP-wnci17Yh3oXeChXg
127.0.0.1	FALSE	/	FALSE	1791937867	visits	2

$ curl -s -b cookie.txt http://127.0.0.1:8000/api/me
{
  "user": "利用者01",
  "pinned": null
}

$ curl -s -b old-cookie.txt http://127.0.0.1:8000/api/me     # ログアウトした後
{
  "detail": "ログインしていません"
}
```

- `cookie.txt` の列は、ドメイン・サブドメインにも送るか・パス・https だけか・期限（UNIX 時刻）・名前・値。`HttpOnly` の Cookie は行頭に `#HttpOnly_` が付く
- 「アプリケーション」→「Cookie」: `session_id` は HttpOnly と SameSite（Lax）に印、`visits` は SameSite だけ
- コンソールの `document.cookie` は `'visits=3'`

## 4. CSRF

| 押したページ | `POST /pin` | 要求の Cookie | 画面 |
| --- | --- | --- | --- |
| `http://127.0.0.1:8000/`（本人のフォーム） | 303 | あり | ピン留めしたタスク: 牛乳を買う |
| `http://127.0.0.1:8001/trap` | 403 | あり（同じサイト） | CSRF トークンが正しくありません |
| `http://localhost:8001/trap` | 401 | なし（別のサイト） | ログインしていません |

## 5. Web API と JSON

```text
$ curl -si -X POST -H 'Content-Type: application/json' -d '{"title": "傘を持っていく"}' http://127.0.0.1:8000/api/tasks
HTTP/1.1 201 Created
Server: WebDemo/1.0
Date: Tue, 13 Oct 2026 00:34:49 GMT
Location: /api/tasks/3
Vary: Origin
Content-Type: application/json
Content-Length: 67

{
  "id": 3,
  "title": "傘を持っていく",
  "done": false
}
```

わざと失敗させたときの結果です。

| 送ったもの | ステータス | `detail` |
| --- | --- | --- |
| フォームの形（`-d 'title=x'`） | 415 Unsupported Media Type | Content-Type は application/json にしてください |
| 閉じていない JSON | 400 Bad Request | JSON として読めません |
| 空のタイトル | 422 Unprocessable Entity | title は1〜100文字の文字列にしてください |
| `DELETE /api/tasks` | 405 Method Not Allowed（`Allow: GET, POST`） | この URL で使えるメソッドは GET, POST です |
| `GET /api/tasks/99` | 404 Not Found | タスクが見つかりません |

- 422 の説明の文字は Python の版で違う（3.12 は `Unprocessable Entity`、3.13 以降は `Unprocessable Content`）
- 公開 API（JSONPlaceholder）の `/todos/1` には `cache-control: max-age=43200`（12時間は確かめずに使ってよい）と `etag` がある。POST は `201` と `location: https://jsonplaceholder.typicode.com/todos/201` を返すが、保存はしないのでその URL は 404

## 6. CORS

```text
（localhost:8001 のコンソール）
> await fetch("http://127.0.0.1:8000/api/me")
Access to fetch at 'http://127.0.0.1:8000/api/me' from origin 'http://localhost:8001' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
Uncaught TypeError: Failed to fetch

（ターミナル①のログ: リクエストは届いている）
[8000] 09:32:47 "GET /api/me HTTP/1.1" 401  Origin: http://localhost:8001  Cookie: なし
[8000] 09:32:47 "GET /api/tasks HTTP/1.1" 200  Origin: http://localhost:8001  Cookie: なし
```

## 7. DOM・fetch・XSS

| 操作 | 結果 |
| --- | --- |
| `textContent` に `<img src=x onerror=alert(1)>` | 一覧の1行目にタグの文字がそのまま出る |
| `innerHTML` に同じ文字列 | ダイアログ `1`（壊れた画像の `onerror` が動いた） |
| `/search-unsafe?q=<img src=x onerror=alert(document.cookie)>` | ダイアログ `visits=6` など。`session_id` は出ない |
| `/search?q=` に同じ文字列 | 見出しが「「<img src=x onerror=alert(document.cookie)>」を含むタスク」で、文字のまま |
