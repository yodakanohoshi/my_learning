"""第1回の演習用ログ（TODO アプリのアプリログ1週間分）を生成する。

乱数シードを固定しているので、何度実行しても同じファイルができる。
講師用メモ（docs/session01/instructor.md）の解答はこの出力から数えたもの。

仕込んである傾向:
- 2026-04-03 の 12 時台に「database is locked」が集中する（バックアップ処理と重なった想定）
- INFO 行にも小文字の "error" を含む URL（/help/error-codes）があり、
  grep -i error で数えると ERROR の件数より多くなる
- WARN 行にも "database is locked" を含むもの（リトライで回復）があり、
  grep 'database is locked' だけでは ERROR の件数より多くなる
- 土日（04-04, 04-05）は使う人が少ないのでログが少ない
- logs/old/ に前週の圧縮前ログが1つあり、find の発展課題で使う

使い方: python scripts/generate_session01_logs.py
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "docs" / "session01" / "assets" / "logs"
SEED = 20260401
FIRST_DAY = datetime(2026, 4, 1)
DAYS = 7
SPIKE_DAY = datetime(2026, 4, 3)

PATHS = ["/", "/", "/", "/", "/?overdue=1"]


def user() -> str:
    return f"U{random.randint(1, 40):03d}"


def task_id() -> str:
    return str(random.randint(1, 500))


def line(ts: datetime, level: str, component: str, message: str) -> str:
    return f"{ts:%Y-%m-%d %H:%M:%S} {level:<5} [{component}] {message}"


def normal_event(ts: datetime) -> str:
    r = random.random()
    ms = random.randint(3, 80)
    if r < 0.55:
        return line(ts, "INFO", "web", f"GET {random.choice(PATHS)} 200 {ms}ms user={user()}")
    if r < 0.70:
        return line(ts, "INFO", "task", f"task created id={task_id()} user={user()}")
    if r < 0.83:
        return line(ts, "INFO", "task", f"task done id={task_id()} user={user()}")
    if r < 0.87:
        return line(ts, "INFO", "web", f"GET /help/error-codes 200 {ms}ms user={user()}")
    if r < 0.92:
        return line(
            ts, "WARN", "task", f"overdue id={task_id()} user={user()} days={random.randint(1, 20)}"
        )
    if r < 0.94:
        return line(ts, "WARN", "db", "database is locked, retrying (1/3)")
    if r < 0.965:
        return line(ts, "ERROR", "db", "database is locked")
    if r < 0.985:
        tid = task_id()
        return line(ts, "ERROR", "web", f"POST /tasks/{tid}/done 404 task not found user={user()}")
    return line(ts, "ERROR", "mail", "SMTP connection timed out host=mail.example.com")


def day_lines(day: datetime) -> list[str]:
    events: list[tuple[datetime, str]] = []
    ts = day.replace(hour=8, minute=30)
    end = day.replace(hour=19, minute=0)
    max_gap = 2400 if day.weekday() >= 5 else 240
    while ts < end:
        ts += timedelta(seconds=random.randint(20, max_gap))
        events.append((ts, normal_event(ts)))
    events.append(
        (day.replace(hour=8, minute=0), line(day.replace(hour=8), "INFO", "app", "started"))
    )
    if day == SPIKE_DAY:
        noon = day.replace(hour=12)
        events.append((noon, line(noon, "INFO", "backup", "backup started")))
        for _ in range(25):
            t = noon + timedelta(seconds=random.randint(5, 3500))
            events.append((t, line(t, "ERROR", "db", "database is locked")))
        done = noon + timedelta(minutes=59, seconds=50)
        events.append((done, line(done, "INFO", "backup", "backup finished")))
    events.sort(key=lambda e: e[0])
    return [text for _, text in events]


def write(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    random.seed(SEED)
    for i in range(DAYS):
        day = FIRST_DAY + timedelta(days=i)
        write(OUT_DIR / f"todo-app-{day:%Y-%m-%d}.log", day_lines(day))
    last_week = FIRST_DAY - timedelta(days=1)
    write(OUT_DIR / "old" / f"todo-app-{last_week:%Y-%m-%d}.log", day_lines(last_week))
    print(f"{OUT_DIR.relative_to(ROOT)} に {DAYS + 1} ファイルを生成しました")


if __name__ == "__main__":
    main()
