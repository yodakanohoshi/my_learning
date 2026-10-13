"""Web 版の入口（uvicorn todo.web:app）。URL と返すものは API設計書のとおり。"""

import os
from collections.abc import Iterator
from datetime import date
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from todo.models import Status, Task, parse_due, sort_by_due, validate_title
from todo.sqlite_store import SqliteStore
from todo.store import TaskStore

PACKAGE_DIR = Path(__file__).parent
DEFAULT_DB_PATH = "var/todo.db"

app = FastAPI(title="TODO アプリ")
app.mount("/static", StaticFiles(directory=PACKAGE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=PACKAGE_DIR / "templates")
# {% ... %} の行が空行として残らないようにする（返す HTML を読みやすくする）
templates.env.trim_blocks = True
templates.env.lstrip_blocks = True


# ---- 依存関係（テストでは app.dependency_overrides で差し替える） ----


def get_store() -> Iterator[TaskStore]:
    """リクエストごとに DB を開き、レスポンスを返したら閉じる。"""
    store = SqliteStore.open(Path(os.environ.get("TODO_DB_PATH", DEFAULT_DB_PATH)))
    try:
        yield store
    finally:
        store.close()


def get_today() -> date:
    """今日の日付。期限切れの判定に使う。"""
    return date.today()


StoreDep = Annotated[TaskStore, Depends(get_store)]
TodayDep = Annotated[date, Depends(get_today)]


# ---- 画面 ----


def visible_tasks(store: TaskStore, today: date, overdue_only: bool) -> list[Task]:
    """一覧に出すタスク。期限が近い順に並べ、overdue_only なら期限切れだけにする。"""
    tasks = sort_by_due(store.list_all())
    if overdue_only:
        tasks = [t for t in tasks if t.status(today) is Status.OVERDUE]
    return tasks


def render_index(
    request: Request,
    store: TaskStore,
    today: date,
    *,
    overdue_only: bool = False,
    error: str | None = None,
    form: dict[str, str] | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    """一覧ページ。エラーのときは error に文言、form に入力された値を入れて返す。"""
    context = {
        "tasks": visible_tasks(store, today, overdue_only),
        "today": today,
        "overdue_only": overdue_only,
        "error": error,
        "form": form or {"title": "", "due": ""},
    }
    return templates.TemplateResponse(request, "index.html", context, status_code=status_code)


# ---- URL ごとの処理（API設計書 1章） ----


@app.get("/", response_class=HTMLResponse)
def index(request: Request, store: StoreDep, today: TodayDep, overdue: str = "") -> HTMLResponse:
    """A-01 一覧ページ。?overdue=1 なら期限切れだけ。"""
    return render_index(request, store, today, overdue_only=overdue == "1")


# 手順4: ここに add_task（A-02 追加）を書く（グリーン）


# 手順6: ここに mark_done（A-03 完了）を書く（グリーン）
