

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
