"""第3回のデモのサーバ: HTTP のヘッダ、Cookie とセッション、CSRF、Web API と JSON、CORS を試す。

標準ライブラリだけで動く（Ubuntu に最初から入っている python3 で起動する）。

起動:   python3 ~/handsoff/docs/session03/assets/web_demo.py
止める: Ctrl+C

2つのサイトを同時に立てる。
- http://127.0.0.1:8000  このサイト（ログイン・ピン留め・タスクの Web API）
- http://localhost:8001  別のサイト（罠のページ /trap、CORS を試すページ）
  127.0.0.1:8001 で開くと「オリジンは違うが、サイトは同じ」になる（サイトはポートを見ない）

データはメモリに置くだけで、止めると消える。パスワードの確認は省いている
（本物のログインでは、ここでパスワードや社内の認証を確かめる）。
"""

import argparse
import hashlib
import html
import itertools
import json
import secrets
import sys
import threading
import time
from dataclasses import asdict, dataclass
from http import HTTPStatus
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlsplit

HOST = "127.0.0.1"

USERS = ("利用者01", "利用者02", "利用者03")
SESSION_SECONDS = 30 * 60
TITLE_MAX = 100

STYLE_CSS = b"""body { font-family: sans-serif; max-width: 40rem; margin: 2rem auto; }
code { background: #eee; padding: 0 .2rem; }
.done { color: #888; text-decoration: line-through; }
.note { color: #555; font-size: .9rem; }
"""


@dataclass
class Ports:
    """ポート番号。使われていて起動できないときは --port・--other-port で変える。"""

    site: int = 8000
    other: int = 8001

    @property
    def site_origin(self) -> str:
        return f"http://127.0.0.1:{self.site}"

    @property
    def allowed_origin(self) -> str:
        # /api/tasks だけ、このオリジンの JavaScript に読ませてよいことにする（CORS）
        return f"http://localhost:{self.other}"


@dataclass
class Task:
    id: int
    title: str
    done: bool = False


@dataclass
class Session:
    user: str
    csrf_token: str
    expires: float
    pinned: str | None = None


PORTS = Ports()
# 複数のリクエストを同時に処理するので、データを触るときはロックを取る
LOCK = threading.Lock()
TASKS: dict[int, Task] = {1: Task(1, "牛乳を買う"), 2: Task(2, "本を返す", done=True)}
NEXT_ID = itertools.count(3)
# セッションの中身はサーバに置く。ブラウザに渡すのは、中身を引くための番号（セッション ID）だけ
SESSIONS: dict[str, Session] = {}


def make_etag(body: bytes) -> str:
    """本文から作った指紋。中身が同じなら同じ値になる。"""
    return '"' + hashlib.sha256(body).hexdigest()[:16] + '"'


def to_json(data: Any) -> bytes:
    return json.dumps(data, ensure_ascii=False, indent=2).encode() + b"\n"


def page(title: str, body: str) -> bytes:
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
{body}
</body>
</html>
""".encode()


def task_items(tasks: list[Task], *, escape: bool = True) -> str:
    def text(s: str) -> str:
        return html.escape(s) if escape else s

    items = "".join(
        f'  <li id="task-{t.id}" class="{"done" if t.done else "todo"}">{text(t.title)}</li>\n'
        for t in tasks
    )
    return f'<ul id="task-list">\n{items}</ul>'


class DemoHandler(BaseHTTPRequestHandler):
    """2つのサイトに共通の部品。応答の組み立てとログの形を決める。"""

    protocol_version = "HTTP/1.1"
    server_version = "WebDemo/1.0"
    body = b""  # リクエストの本文（handle_any で読む）

    def version_string(self) -> str:
        return self.server_version  # Server ヘッダに Python の版を出さない

    # --- 応答を返す ---

    def send(
        self,
        status: HTTPStatus,
        body: bytes = b"",
        content_type: str = "text/html; charset=utf-8",
        headers: list[tuple[str, str]] | None = None,
    ) -> None:
        self.send_response(status)
        for name, value in headers or []:
            self.send_header(name, value)
        no_body = status in (HTTPStatus.NO_CONTENT, HTTPStatus.NOT_MODIFIED)
        if body and not no_body:
            self.send_header("Content-Type", content_type)
        if status != HTTPStatus.NO_CONTENT:
            self.send_header("Content-Length", str(0 if no_body else len(body)))
        self.end_headers()
        if self.command != "HEAD" and not no_body:
            self.wfile.write(body)

    def send_page(
        self,
        status: HTTPStatus,
        title: str,
        body: str,
        headers: list[tuple[str, str]] | None = None,
    ) -> None:
        self.send(
            status, page(title, body), headers=[("Cache-Control", "no-store"), *(headers or [])]
        )

    def send_json(
        self, status: HTTPStatus, data: Any, headers: list[tuple[str, str]] | None = None
    ) -> None:
        self.send(status, to_json(data), "application/json", headers)

    def redirect(self, location: str, headers: list[tuple[str, str]] | None = None) -> None:
        # 303 See Other: 「次はこの URL を GET してください」
        self.send(HTTPStatus.SEE_OTHER, headers=[("Location", location), *(headers or [])])

    # --- リクエストを読む ---

    def cookies(self) -> dict[str, str]:
        jar: SimpleCookie = SimpleCookie()
        try:
            jar.load(self.headers.get("Cookie", ""))
        except CookieError:
            return {}
        return {name: morsel.value for name, morsel in jar.items()}

    def read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length > 0 else b""

    def read_form(self) -> dict[str, str]:
        fields = parse_qs(self.body.decode(errors="replace"))
        return {name: values[0] for name, values in fields.items()}

    # --- キャッシュ: ETag と 304 ---

    def send_with_etag(
        self, body: bytes, content_type: str, headers: list[tuple[str, str]]
    ) -> None:
        # Cache-Control: no-cache は「手元のコピーを使う前に、毎回サーバに確かめる」
        etag = make_etag(body)
        headers = [("ETag", etag), ("Cache-Control", "no-cache"), *headers]
        if self.headers.get("If-None-Match") == etag:
            self.send(HTTPStatus.NOT_MODIFIED, headers=headers)  # 変わっていないので本文なし
            return
        self.send(HTTPStatus.OK, body, content_type, headers)

    def style_css(self) -> None:
        self.send_with_etag(STYLE_CSS, "text/css; charset=utf-8", [])

    # --- ログ: 誰から（Origin）、Cookie が付いていたかも出す ---

    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        if isinstance(code, HTTPStatus):
            code = code.value
        headers = getattr(self, "headers", None)  # 1行目から読めなかったときはない
        origin = headers.get("Origin", "なし") if headers else "なし"
        cookie = "あり" if headers and headers.get("Cookie") else "なし"
        self.log_message('"%s" %s  Origin: %s  Cookie: %s', self.requestline, code, origin, cookie)

    def log_message(self, format: str, *args: Any) -> None:
        port = self.connection.getsockname()[1]
        stamp = time.strftime("%H:%M:%S")
        sys.stderr.write(f"[{port}] {stamp} {format % args}\n")

    # どのメソッドも本文を読んでから route() に回す（使えないメソッドは route() が 405 を返す）。
    # 本文を読み残すと、同じ接続の次のリクエストとして読まれてしまう
    def handle_any(self) -> None:
        self.body = self.read_body()
        self.route()

    do_GET = do_HEAD = do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = handle_any  # noqa: N815

    def route(self) -> None:
        raise NotImplementedError


class SiteHandler(DemoHandler):
    """このサイト（127.0.0.1:8000）。"""

    def route(self) -> None:
        url = urlsplit(self.path)
        query = {name: values[0] for name, values in parse_qs(url.query).items()}
        method = "GET" if self.command == "HEAD" else self.command
        path = url.path
        if path == "/api/tasks" or path.startswith("/api/tasks/"):
            self.tasks_api(method, path.removeprefix("/api/tasks").strip("/"), query)
            return
        match (method, path):
            case ("GET", "/"):
                self.top_page()
            case ("GET", "/static/style.css"):
                self.style_css()
            case ("GET", "/headers"):
                self.echo_headers()
            case ("GET", "/search"):
                self.search_page(query.get("q", ""), escape=True)
            case ("GET", "/search-unsafe"):
                self.search_page(query.get("q", ""), escape=False)
            case ("POST", "/login"):
                self.login()
            case ("POST", "/logout"):
                self.logout()
            case ("POST", "/pin"):
                self.pin()
            case ("GET", "/api/me"):
                self.api_me()
            case _:
                self.send_page(HTTPStatus.NOT_FOUND, "見つかりません", "<p>見つかりません</p>")

    # --- セッション ---

    def current_session(self) -> Session | None:
        session_id = self.cookies().get("session_id")
        if not session_id:
            return None
        with LOCK:
            session = SESSIONS.get(session_id)
            if session is not None and session.expires < time.time():
                del SESSIONS[session_id]  # サーバ側でも期限を見る
                return None
            return session

    def login(self) -> None:
        user = self.read_form().get("user", "")
        if user not in USERS:
            self.send_page(HTTPStatus.BAD_REQUEST, "ログイン", "<p>利用者を選んでください</p>")
            return
        session_id = secrets.token_urlsafe(16)  # 推測できない乱数にする
        with LOCK:
            SESSIONS[session_id] = Session(
                user=user,
                csrf_token=secrets.token_urlsafe(16),
                expires=time.time() + SESSION_SECONDS,
            )
        # HttpOnly: JavaScript から読めない（XSS で盗まれにくい）
        # SameSite=Lax: ほかのサイトから送られた POST には Cookie を付けない（CSRF の被害を減らす）
        cookie = (
            f"session_id={session_id}; HttpOnly; Path=/; SameSite=Lax; Max-Age={SESSION_SECONDS}"
        )
        self.redirect("/", [("Set-Cookie", cookie)])

    def logout(self) -> None:
        session_id = self.cookies().get("session_id")
        if session_id:
            with LOCK:
                SESSIONS.pop(session_id, None)  # サーバ側のセッションを消す
        # Max-Age=0 で、ブラウザに Cookie を消させる
        self.redirect("/", [("Set-Cookie", "session_id=; Path=/; Max-Age=0")])

    def pin(self) -> None:
        form = self.read_form()
        session = self.current_session()
        if session is None:
            self.send_page(HTTPStatus.UNAUTHORIZED, "ピン留め", "<p>ログインしていません</p>")
            return
        # Cookie はブラウザが自動で付けるので、Cookie だけでは「本人が押したか」はわからない。
        # ページに埋め込んだトークンが一致することで、このサイトのフォームから送られたと確かめる
        if not secrets.compare_digest(form.get("csrf_token", ""), session.csrf_token):
            body = "<p>CSRF トークンが正しくありません</p>"
            self.send_page(HTTPStatus.FORBIDDEN, "ピン留め", body)
            return
        with LOCK:
            session.pinned = form.get("title", "")
        self.redirect("/")

    def api_me(self) -> None:
        # CORS の許可のヘッダを付けない API（ほかのオリジンの JavaScript には読ませない）
        session = self.current_session()
        if session is None:
            self.send_json(HTTPStatus.UNAUTHORIZED, {"detail": "ログインしていません"})
            return
        self.send_json(HTTPStatus.OK, {"user": session.user, "pinned": session.pinned})

    # --- ページ ---

    def top_page(self) -> None:
        # visits は HttpOnly を付けない Cookie。中身をブラウザが持つので、利用者が書き換えられる
        raw = self.cookies().get("visits", "0")
        visits = int(raw) + 1 if raw.isdigit() else 1
        session = self.current_session()
        if session is None:
            options = "".join(f'<option value="{u}">{u}</option>' for u in USERS)
            account = f"""<p>ログインしていません。</p>
<form method="post" action="/login">
  <label>利用者 <select name="user">{options}</select></label>
  <button type="submit">ログイン</button>
</form>"""
        else:
            pinned = html.escape(session.pinned or "（なし）")
            # CSRF 対策のトークン。このページを開いた本人のフォームにだけ入っている
            account = f"""<p>ログイン中: <strong>{html.escape(session.user)}</strong></p>
<p>ピン留めしたタスク: {pinned}</p>
<form method="post" action="/pin">
  <input type="hidden" name="csrf_token" value="{html.escape(session.csrf_token)}">
  <button type="submit" name="title" value="牛乳を買う">「牛乳を買う」をピン留め</button>
</form>
<form method="post" action="/logout"><button type="submit">ログアウト</button></form>"""
        with LOCK:
            tasks = list(TASKS.values())
        body = f"""<h1>Web 通信のデモ（{PORTS.site}）</h1>
<p class="note">このページを開いた回数（Cookie の visits）: {visits}</p>
<h2>ログイン</h2>
{account}
<h2>タスク（/api/tasks と同じデータ）</h2>
{task_items(tasks)}
<form action="/search"><input name="q" placeholder="検索"><button>検索</button></form>
<h2>リンク</h2>
<ul>
  <li><a href="/headers">/headers</a>: ブラウザが送ったリクエストヘッダを JSON で返す</li>
  <li><a href="/api/tasks">/api/tasks</a>: タスクの Web API（JSON）</li>
  <li><a href="/api/me">/api/me</a>: ログイン中の利用者（JSON）</li>
</ul>"""
        cookie = f"visits={visits}; Path=/; Max-Age=86400; SameSite=Lax"
        self.send_page(HTTPStatus.OK, "Web 通信のデモ", body, [("Set-Cookie", cookie)])

    def search_page(self, q: str, *, escape: bool) -> None:
        with LOCK:
            hits = [t for t in TASKS.values() if q in t.title]
        # escape=False は XSS の体験用。入力をそのまま HTML に入れてしまう悪い例
        shown = html.escape(q) if escape else q
        body = f"""<h1>「{shown}」を含むタスク</h1>
{task_items(hits, escape=escape)}
<p><a href="/">トップへ</a></p>"""
        self.send_page(HTTPStatus.OK, "検索", body)

    def echo_headers(self) -> None:
        data = {"method": self.command, "path": self.path, "headers": dict(self.headers.items())}
        self.send_json(HTTPStatus.OK, data)

    # --- タスクの Web API ---

    def cors_headers(self) -> list[tuple[str, str]]:
        headers = [("Vary", "Origin")]
        if self.headers.get("Origin") == PORTS.allowed_origin:
            headers.append(("Access-Control-Allow-Origin", PORTS.allowed_origin))
        return headers

    def tasks_api(self, method: str, rest: str, query: dict[str, str]) -> None:
        cors = self.cors_headers()
        if method == "OPTIONS":
            # プリフライト: ほかのオリジンから JSON を POST する前に、ブラウザが確かめに来る
            self.send(
                HTTPStatus.NO_CONTENT,
                headers=[
                    *cors,
                    ("Access-Control-Allow-Methods", "GET, POST"),
                    ("Access-Control-Allow-Headers", "Content-Type"),
                ],
            )
            return
        if rest == "":
            match method:
                case "GET":
                    self.list_tasks(query, cors)
                case "POST":
                    self.create_task(cors)
                case _:
                    self.method_not_allowed("GET, POST", cors)
            return
        task_id = int(rest) if rest.isdigit() else -1
        with LOCK:
            task = TASKS.get(task_id)
        if task is None:
            self.send_json(HTTPStatus.NOT_FOUND, {"detail": "タスクが見つかりません"}, cors)
            return
        match method:
            case "GET":
                self.send_with_etag(to_json(asdict(task)), "application/json", cors)
            case "PATCH":
                self.update_task(task, cors)
            case "DELETE":
                with LOCK:
                    TASKS.pop(task.id, None)
                self.send(HTTPStatus.NO_CONTENT, headers=cors)
            case _:
                self.method_not_allowed("GET, PATCH, DELETE", cors)

    def method_not_allowed(self, allow: str, cors: list[tuple[str, str]]) -> None:
        detail = {"detail": f"この URL で使えるメソッドは {allow} です"}
        self.send_json(HTTPStatus.METHOD_NOT_ALLOWED, detail, [("Allow", allow), *cors])

    def list_tasks(self, query: dict[str, str], cors: list[tuple[str, str]]) -> None:
        with LOCK:
            tasks = list(TASKS.values())
        if "done" in query:  # ?done=true・?done=false で絞り込む
            tasks = [t for t in tasks if t.done == (query["done"] == "true")]
        self.send_with_etag(to_json([asdict(t) for t in tasks]), "application/json", cors)

    def read_json(self, cors: list[tuple[str, str]]) -> dict[str, Any] | None:
        """本文を JSON として読む。読めなければエラーを返して None。"""
        if self.headers.get_content_type() != "application/json":
            detail = {"detail": "Content-Type は application/json にしてください"}
            self.send_json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail, cors)
            return None
        try:
            data = json.loads(self.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(HTTPStatus.BAD_REQUEST, {"detail": "JSON として読めません"}, cors)
            return None
        if not isinstance(data, dict):
            detail = {"detail": "JSON のオブジェクト（{...}）で送ってください"}
            self.send_json(HTTPStatus.UNPROCESSABLE_ENTITY, detail, cors)
            return None
        return data

    def valid_title(self, title: Any, cors: list[tuple[str, str]]) -> str | None:
        if isinstance(title, str) and 0 < len(title.strip()) <= TITLE_MAX:
            return title.strip()
        detail = {"detail": f"title は1〜{TITLE_MAX}文字の文字列にしてください"}
        self.send_json(HTTPStatus.UNPROCESSABLE_ENTITY, detail, cors)
        return None

    def create_task(self, cors: list[tuple[str, str]]) -> None:
        data = self.read_json(cors)
        if data is None:
            return
        title = self.valid_title(data.get("title"), cors)
        if title is None:
            return
        with LOCK:
            task = Task(next(NEXT_ID), title)
            TASKS[task.id] = task
        # 201 Created: 作ったものの URL を Location で知らせる
        location = [("Location", f"/api/tasks/{task.id}"), *cors]
        self.send_json(HTTPStatus.CREATED, asdict(task), location)

    def update_task(self, task: Task, cors: list[tuple[str, str]]) -> None:
        # PATCH: 送った項目だけを変える（部分更新）
        data = self.read_json(cors)
        if data is None:
            return
        if "done" in data and not isinstance(data["done"], bool):
            detail = {"detail": "done は true か false にしてください"}
            self.send_json(HTTPStatus.UNPROCESSABLE_ENTITY, detail, cors)
            return
        title = task.title
        if "title" in data:
            checked = self.valid_title(data["title"], cors)
            if checked is None:
                return
            title = checked
        with LOCK:
            task.title = title
            task.done = data.get("done", task.done)
        self.send_json(HTTPStatus.OK, asdict(task), cors)


class OtherSiteHandler(DemoHandler):
    """別のサイト（localhost:8001）。罠のページと、CORS を試すコンソールの置き場所。"""

    def route(self) -> None:
        path = urlsplit(self.path).path
        host = html.escape(self.headers.get("Host", ""))
        if self.command in ("GET", "HEAD") and path == "/":
            body = f"""<h1>別のサイト（{host}）</h1>
<p>このページの開発者ツールのコンソールから、{PORTS.site_origin} に fetch して CORS を試す。</p>
<p><a href="/trap">プレゼントのページ</a></p>"""
            self.send_page(HTTPStatus.OK, "別のサイト", body)
        elif self.command in ("GET", "HEAD") and path == "/static/style.css":
            self.style_css()
        elif self.command in ("GET", "HEAD") and path == "/trap":
            # ほかのサイトに置かれた罠のページ。トークンを知らないまま /pin へ送らせる
            body = f"""<h1>プレゼントが当たりました（{host}）</h1>
<form method="post" action="{PORTS.site_origin}/pin">
  <button type="submit" name="title" value="罠で仕込んだタスク">受け取る</button>
</form>"""
            self.send_page(HTTPStatus.OK, "プレゼント", body)
        else:
            self.send_page(HTTPStatus.NOT_FOUND, "見つかりません", "<p>見つかりません</p>")


def main() -> None:
    parser = argparse.ArgumentParser(description="第3回のデモのサーバ")
    parser.add_argument("--port", type=int, default=PORTS.site, help="このサイトのポート")
    parser.add_argument("--other-port", type=int, default=PORTS.other, help="別のサイトのポート")
    args = parser.parse_args()
    PORTS.site, PORTS.other = args.port, args.other_port
    servers = [
        ThreadingHTTPServer((HOST, PORTS.site), SiteHandler),
        ThreadingHTTPServer((HOST, PORTS.other), OtherSiteHandler),
    ]
    threading.Thread(target=servers[1].serve_forever, daemon=True).start()
    print(f"このサイト: {PORTS.site_origin}/")
    print(f"別のサイト: {PORTS.allowed_origin}/ （127.0.0.1:{PORTS.other} でも開ける）")
    print("止めるときは Ctrl+C", flush=True)
    try:
        servers[0].serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for server in servers:
            server.server_close()


if __name__ == "__main__":
    main()
