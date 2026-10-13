"""Web 版の入口（uvicorn todo.web:app）。URL と返すものは API設計書のとおり。"""

import os
from collections.abc import Iterator
from datetime import date
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from todo.models import InvalidTaskError, Status, Task, parse_due, sort_by_due, validate_title
from todo.sqlite_store import SqliteStore
from todo.store import TaskNotFoundError, TaskStore

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


def overdue_query(overdue_only: bool) -> str:
    """断片の URL に付けるクエリ。期限切れだけの表示中は、断片も期限切れだけにする（BUG-001）。"""
    return "?overdue=1" if overdue_only else ""


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
        "query": overdue_query(overdue_only),
        "error": error,
        "form": form or {"title": "", "due": ""},
    }
    return templates.TemplateResponse(request, "index.html", context, status_code=status_code)


# ---- URL ごとの処理（API設計書 1章） ----


@app.get("/", response_class=HTMLResponse)
def index(request: Request, store: StoreDep, today: TodayDep, overdue: str = "") -> HTMLResponse:
    """A-01 一覧ページ。?overdue=1 なら期限切れだけ。"""
    return render_index(request, store, today, overdue_only=overdue == "1")


@app.post("/tasks", response_model=None)
def add_task(
    request: Request,
    store: StoreDep,
    today: TodayDep,
    title: Annotated[str, Form()] = "",
    due: Annotated[str, Form()] = "",
) -> HTMLResponse | RedirectResponse:
    """A-02 追加。入力のチェックは CLI と同じ関数（models.py）を使う。"""
    try:
        store.add(validate_title(title), parse_due(due))
    except InvalidTaskError as e:
        form = {"title": title, "due": due}
        return render_index(request, store, today, error=str(e), form=form, status_code=400)
    # POST → リダイレクト → GET にして、再読み込みで二重に追加されないようにする
    return RedirectResponse("/", status_code=303)


@app.post("/tasks/{task_id}/done", response_model=None)
def mark_done(
    request: Request, task_id: int, store: StoreDep, today: TodayDep
) -> HTMLResponse | RedirectResponse:
    """A-03 完了。"""
    try:
        store.mark_done(task_id)
    except TaskNotFoundError:
        return render_index(request, store, today, error="タスクが見つかりません", status_code=404)
    return RedirectResponse("/", status_code=303)


# ---- HTML 断片を返す URL（第12回。API設計書 A-04〜A-06） ----


def render_task_list(
    request: Request, store: TaskStore, today: date, *, overdue_only: bool
) -> HTMLResponse:
    """一覧（<ul id="task-list">）だけの HTML 断片。"""
    context = {
        "tasks": visible_tasks(store, today, overdue_only),
        "today": today,
        "query": overdue_query(overdue_only),
    }
    return templates.TemplateResponse(request, "_task_list.html", context)


@app.get("/fragments/tasks", response_class=HTMLResponse)
def task_list_fragment(
    request: Request, store: StoreDep, today: TodayDep, overdue: str = ""
) -> HTMLResponse:
    """A-04 一覧の断片。"""
    return render_task_list(request, store, today, overdue_only=overdue == "1")


def render_error(request: Request, error: str, status_code: int) -> HTMLResponse:
    """エラーの文言だけの HTML 断片（<p class="error">）。"""
    return templates.TemplateResponse(
        request, "_error.html", {"error": error}, status_code=status_code
    )


@app.post("/fragments/tasks", response_class=HTMLResponse)
def add_task_fragment(
    request: Request,
    store: StoreDep,
    today: TodayDep,
    title: Annotated[str, Form()] = "",
    due: Annotated[str, Form()] = "",
    overdue: str = "",
) -> HTMLResponse:
    """A-05 追加して一覧の断片を返す。入力エラーなら 400 でエラーの断片。"""
    try:
        store.add(validate_title(title), parse_due(due))
    except InvalidTaskError as e:
        return render_error(request, str(e), 400)
    return render_task_list(request, store, today, overdue_only=overdue == "1")


@app.post("/fragments/tasks/{task_id}/done", response_class=HTMLResponse)
def mark_done_fragment(
    request: Request, task_id: int, store: StoreDep, today: TodayDep, overdue: str = ""
) -> HTMLResponse:
    """A-06 完了にして一覧の断片を返す。ない id なら 404 でエラーの断片。"""
    try:
        store.mark_done(task_id)
    except TaskNotFoundError:
        return render_error(request, "タスクが見つかりません", 404)
    return render_task_list(request, store, today, overdue_only=overdue == "1")


# ---- 比較用: JSON を返す URL（API設計書 A-07） ----


class DoneOut(BaseModel):
    id: int
    done: bool


@app.post("/api/tasks/{task_id}/done")
def mark_done_json(task_id: int, store: StoreDep) -> DoneOut:
    """A-07 完了にして JSON を返す。画面の組み立てはブラウザ側（static/done-json.js）がする。"""
    try:
        task = store.mark_done(task_id)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail="タスクが見つかりません") from e
    return DoneOut(id=task.id, done=task.done)
