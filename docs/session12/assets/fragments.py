

# ---- HTML 断片を返す URL（第12回。API設計書 A-04〜A-06） ----


def render_task_list(
    request: Request, store: TaskStore, today: date, *, overdue_only: bool
) -> HTMLResponse:
    """一覧（<ul id="task-list">）だけの HTML 断片。"""
    context = {
        "tasks": visible_tasks(store, today, overdue_only),
        "today": today,
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
