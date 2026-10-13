"""資料の形式を検査する。

- 全回に受講者用（README.md）と講師用（instructor.md）がある
- 冒頭4行（タイトル・tag・前提タグ・所要）がそろっている
- tag と所要がカリキュラムの「全N回の一覧」と一致し、前提タグが知識体系マップにある
- 一覧の所要が「名前N分」を「 / 」でつないだ形で、合計60分になっている
- 必須の見出しがそろっている
- `--strict` のときは「（作成中）」が残っていないこと

使い方: python scripts/check_materials.py [--strict]
"""

import sys
from pathlib import Path

from curriculum import (
    DOCS,
    DURATION_PREFIX,
    INSTRUCTOR_SUFFIX,
    SESSION_MINUTES,
    Session,
    duration_minutes,
    h2_headings,
    knowledge_map_tags,
    parse_header,
    read_curriculum,
    sessions,
)

STUDENT_HEADINGS = [
    "ゴール",
    "まとめ",
    "ハンズオン",
    "読む章",
]
INSTRUCTOR_HEADINGS = [
    "進行メモ",
    "つまずきやすい点",
    "解答例",
]
PLACEHOLDER = "（作成中）"


def check_file(
    path: Path, session: Session, known_tags: set[str], instructor: bool, strict: bool
) -> list[str]:
    if not path.exists():
        return [f"{path.relative_to(DOCS)}: ファイルがありません"]
    errors = []
    rel = path.relative_to(DOCS)
    try:
        header = parse_header(path)
    except ValueError as e:
        return [str(e)]

    expected_title = f"第{session.number}回 {session.theme}"
    if instructor:
        expected_title += INSTRUCTOR_SUFFIX
    if header.title != expected_title:
        errors.append(f"{rel}: タイトルは「# {expected_title}」にしてください")
    if header.tags != session.tags:
        errors.append(
            f"{rel}: tag が一覧と違います（資料: {', '.join(header.tags)} / "
            f"一覧: {', '.join(session.tags)}）"
        )
    for tag in header.prerequisites:
        if tag not in known_tags:
            errors.append(f"{rel}: 前提タグ「{tag}」は知識体系マップにありません")
    expected_duration = DURATION_PREFIX + session.duration
    if header.duration != expected_duration:
        errors.append(f"{rel}: 4行目は「{expected_duration}」にしてください（一覧の所要と同じ）")

    headings = h2_headings(path)
    required = INSTRUCTOR_HEADINGS if instructor else STUDENT_HEADINGS
    missing = [h for h in required if h not in headings]
    if missing:
        errors.append(f"{rel}: 見出しが足りません: {', '.join(missing)}")
    elif [h for h in headings if h in required] != required:
        errors.append(f"{rel}: 見出しの順序は {' → '.join(required)} にしてください")

    if strict and PLACEHOLDER in path.read_text(encoding="utf-8"):
        errors.append(f"{rel}: 「{PLACEHOLDER}」が残っています")
    return errors


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    text = read_curriculum()
    known_tags = set(knowledge_map_tags(text))
    errors = []
    for session in sessions(text):
        for tag in session.tags:
            if tag not in known_tags:
                errors.append(f"curriculum.md: 第{session.number}回のタグ「{tag}」がマップにない")
        try:
            total = sum(minutes for _, minutes in duration_minutes(session.duration))
        except ValueError as e:
            errors.append(f"curriculum.md: 第{session.number}回: {e}")
        else:
            if total != SESSION_MINUTES:
                errors.append(
                    f"curriculum.md: 第{session.number}回の所要の合計が{total}分です"
                    f"（{SESSION_MINUTES}分にする）"
                )
        directory = DOCS / session.dir_name
        errors += check_file(directory / "README.md", session, known_tags, False, strict)
        errors += check_file(directory / "instructor.md", session, known_tags, True, strict)

    for error in errors:
        print(error)
    print(f"{'NG' if errors else 'OK'}: {len(errors)} 件の指摘")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
