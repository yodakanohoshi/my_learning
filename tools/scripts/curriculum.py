"""docs/curriculum.md（正本）と各回の資料を読み取る共通処理。

check_materials.py と build_tag_index.py から使う。正本は読むだけで書き換えない。
"""

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
CURRICULUM = DOCS / "curriculum.md"

DURATION_PREFIX = "所要: "
SESSION_MINUTES = 60
NO_PREREQUISITE = "なし"
INSTRUCTOR_SUFFIX = "（講師用）"


@dataclass(frozen=True)
class Session:
    """カリキュラムの「全N回の一覧」の1行。"""

    number: int
    phase: str
    theme: str
    duration: str
    tags: tuple[str, ...]
    deliverable: str

    @property
    def dir_name(self) -> str:
        return f"session{self.number:02d}"


@dataclass(frozen=True)
class Header:
    """資料冒頭の4行（タイトル・tag・前提タグ・所要）。"""

    title: str
    tags: tuple[str, ...]
    prerequisites: tuple[str, ...]
    duration: str


@dataclass(frozen=True)
class Reading:
    """副読本・参考書・公式資料の表の1行。"""

    title: str
    url: str
    tags: tuple[str, ...]
    usage: str


def _section(text: str, heading: str) -> str:
    """見出し行から、同じかそれより上の階層の次の見出しまでを返す。"""
    lines = text.splitlines()
    level = len(heading) - len(heading.lstrip("#"))
    start = lines.index(heading) + 1
    for i in range(start, len(lines)):
        stripped = lines[i]
        if stripped.startswith("#"):
            other = len(stripped) - len(stripped.lstrip("#"))
            if other <= level:
                return "\n".join(lines[start:i])
    return "\n".join(lines[start:])


def _table_rows(text: str) -> list[list[str]]:
    """Markdown の表から、見出し行と区切り行を除いたセルの一覧を返す。"""
    rows = [line for line in text.splitlines() if line.startswith("|")]
    return [[cell.strip() for cell in row.strip("|").split("|")] for row in rows[2:]]


def _split_tags(cell: str) -> tuple[str, ...]:
    return tuple(tag.strip() for tag in cell.split(",") if tag.strip())


def read_curriculum() -> str:
    return CURRICULUM.read_text(encoding="utf-8")


def knowledge_map_tags(text: str) -> dict[str, str]:
    """知識体系マップのタグ名と説明を、マップに書かれた順で返す。"""
    body = _section(text, "### 知識体系マップ（木構造）")
    tags: dict[str, str] = {}
    for match in re.finditer(r"^\s*- `([^`]+)` (.+)$", body, flags=re.MULTILINE):
        tags[match.group(1)] = match.group(2).strip()
    return tags


def sessions(text: str) -> list[Session]:
    heading = re.search(r"^## 全\d+回の一覧$", text, flags=re.MULTILINE)
    if heading is None:
        raise ValueError("curriculum.md に「## 全N回の一覧」がありません")
    body = _section(text, heading.group(0))
    result = []
    for number, phase, theme, duration, tags, deliverable in _table_rows(body):
        result.append(Session(int(number), phase, theme, duration, _split_tags(tags), deliverable))
    return result


def readings(text: str) -> list[Reading]:
    """副読本・参考書・無料の公式資料の表を、対応タグ付きで返す。"""
    link = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    result = []
    # (見出し, 対応タグの列, 使いどころの列)
    tables = [
        ("### 副読本（紹介のみ。全員が持つ前提ではない）", 3, 4),
        ("### 参考書（リファレンス、1万円以内）", 3, 4),
        ("### 無料の公式資料", 1, 2),
    ]
    for heading, tag_col, usage_col in tables:
        for row in _table_rows(_section(text, heading)):
            match = link.search(row[0])
            if match is None:  # 合計行など
                continue
            title = link.sub(r"\1", row[0])
            result.append(Reading(title, match.group(2), _split_tags(row[tag_col]), row[usage_col]))
    return result


def parse_header(path: Path) -> Header:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 4:
        raise ValueError(f"{path}: 冒頭の4行（タイトル・tag・前提タグ・所要）がありません")
    title, tag_line, prereq_line, duration = lines[:4]
    if not title.startswith("# "):
        raise ValueError(f"{path}: 1行目は「# 第N回 テーマ」にしてください")
    if not tag_line.startswith("tag: "):
        raise ValueError(f"{path}: 2行目は「tag: 」で始めてください")
    if not prereq_line.startswith("前提タグ: "):
        raise ValueError(f"{path}: 3行目は「前提タグ: 」で始めてください")
    prereqs = _split_tags(prereq_line.removeprefix("前提タグ: "))
    if prereqs == (NO_PREREQUISITE,):
        prereqs = ()
    return Header(
        title=title.removeprefix("# "),
        tags=_split_tags(tag_line.removeprefix("tag: ")),
        prerequisites=prereqs,
        duration=duration,
    )


def h2_headings(path: Path) -> list[str]:
    return [
        line.removeprefix("## ").strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("## ")
    ]


def duration_minutes(duration: str) -> list[tuple[str, int]]:
    """「座学20分 / ハンズオン30分」を [(座学, 20), (ハンズオン, 30)] にする。

    形が違えば ValueError。
    """
    result = []
    for part in duration.split(" / "):
        match = re.fullmatch(r"([^\d\s]+)(\d+)分", part)
        if match is None:
            raise ValueError(f"所要の「{part}」は「名前N分」の形にしてください")
        result.append((match.group(1), int(match.group(2))))
    return result


def tag_ancestors(tag: str, known: set[str]) -> list[str]:
    """`http-基本` → [`http`] のように、知識体系マップにある上位タグを返す。"""
    parts = tag.split("-")
    return [p for i in range(1, len(parts)) if (p := "-".join(parts[:i])) in known]


def tag_matches(tag: str, other: str) -> bool:
    """同じタグか、どちらかがもう一方の上位にあたる（`http` と `http-基本` など）。

    副読本の表には `pm` のような知識体系マップにない上位名も出てくるので、前方一致で判定する。
    """
    return tag == other or tag.startswith(other + "-") or other.startswith(tag + "-")
