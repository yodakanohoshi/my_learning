"""研修の全体像の図（build_overview.py）に使うデータを、カリキュラムと各回の資料から組み立てる。

- ジャンルは知識体系マップで大分野の1つ下の枝（タグのない中間の枝があれば、さらに1つ下）
- ジャンルを扱う回は、各回の資料の冒頭の tag から集める
- 横断テーマは、カリキュラムの番号付きリストと、説明に最初に出る「第N回」から取る
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from curriculum import DOCS, _section, parse_header, sessions, tag_ancestors

OUT_DIR = DOCS / "diagrams"
FONT = '"BIZ UDPGothic","Hiragino Sans","Yu Gothic UI","WenQuanYi Zen Hei",sans-serif'
FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link href="https://fonts.googleapis.com/css2?family=BIZ+UDPGothic:wght@400;700&display=swap"'
    ' rel="stylesheet">'
)
INK = "#1b1b1b"

# 大分野ごとの (地の色, 線の色)。マップに書かれた大分野の順に使う
AREA_COLORS = [
    ("#edf1f7", "#2b4c7e"),
    ("#eef4ef", "#3a6b47"),
    ("#f7f1e6", "#9a6b1f"),
    ("#f3eff6", "#634a7a"),
]


@dataclass
class Genre:
    tag: str
    label: str
    area: str
    sessions: set[int] = field(default_factory=set)

    @property
    def span(self) -> tuple[int, int]:
        return min(self.sessions), max(self.sessions)


@dataclass(frozen=True)
class Theme:
    name: str
    start: int


def genres(text: str) -> dict[str, Genre]:
    """知識体系マップから、ジャンルのタグ → Genre を返す（マップに書かれた順）。"""
    body = _section(text, "### 知識体系マップ（木構造）")
    result: dict[str, Genre] = {}
    area = ""
    untagged_group = -1  # タグのない中間の枝の深さ（なければ -1）
    for line in body.splitlines():
        stripped = line.lstrip(" ")
        if not stripped.startswith("- "):
            continue
        depth = (len(line) - len(stripped)) // 4
        if depth == 0:
            area = re.sub(r"\*\*(.+?)\*\*.*", r"\1", stripped[2:])
            untagged_group = -1
            continue
        match = re.match(r"- `([^`]+)` (\S+)", stripped)
        if match is None:  # タグのない中間の枝
            untagged_group = depth
            continue
        if depth == 1 or (untagged_group != -1 and depth == untagged_group + 1):
            label = match.group(2).split("：")[0]
            result[match.group(1)] = Genre(match.group(1), label, area)
    return result


def genre_of(tag: str, known: dict[str, Genre]) -> str | None:
    for candidate in [tag, *reversed(tag_ancestors(tag, set(known)))]:
        if candidate in known:
            return candidate
    return None


def analyze(text: str) -> dict[str, Genre]:
    """ジャンルごとに、扱う回（各回の資料の冒頭の tag）を集める。"""
    known = genres(text)
    for session in sessions(text):
        header = parse_header(DOCS / session.dir_name / "README.md")
        for tag in header.tags:
            if name := genre_of(tag, known):
                known[name].sessions.add(session.number)
    return known


def themes(text: str) -> list[Theme]:
    """横断テーマの番号付きリストから、名前と始まる回（説明に最初に出る「第N回」）を返す。"""
    body = _section(text, "## 通しの題材と横断テーマ")
    result = []
    for match in re.finditer(r"^\d+\. \*\*(.+?)\*\*：(.*)$", body, flags=re.MULTILINE):
        start = re.search(r"第(\d+)回", match.group(2))
        result.append(Theme(match.group(1), int(start.group(1)) if start else 1))
    return result


def phases(text: str) -> list[tuple[str, int, int]]:
    """(フェーズ名, 最初の回, 最後の回)。一覧の「フェーズ」の列が続く範囲をまとめる。"""
    result: list[tuple[str, int, int]] = []
    for s in sessions(text):
        if result and result[-1][0] == s.phase:
            result[-1] = (s.phase, result[-1][1], s.number)
        else:
            result.append((s.phase, s.number, s.number))
    return result


def pack(items: list[Genre]) -> list[tuple[Genre, int]]:
    """横棒が重ならないように、レーンの中の行（1から）を割り当てる（左から詰める）。"""
    rows: list[int] = []  # 各行の最後の回
    placed = []
    for g in sorted(items, key=lambda g: g.span):
        first, last = g.span
        row = next((i for i, end in enumerate(rows) if end < first), len(rows))
        if row == len(rows):
            rows.append(last)
        else:
            rows[row] = last
        placed.append((g, row + 1))
    return placed


def session_list(numbers: set[int]) -> str:
    return "・".join(str(n) for n in sorted(numbers))


def export_images(html_path: Path) -> None:
    """HTML の .slide を、同じ名前の PNG（2倍の解像度）と PDF（1ページ）に書き出す。"""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=2, viewport={"width": 1200, "height": 800})
        page.goto(html_path.resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        slide = page.locator(".slide")
        box = slide.bounding_box()
        assert box is not None
        slide.screenshot(path=str(html_path.with_suffix(".png")))
        page.pdf(
            path=str(html_path.with_suffix(".pdf")),
            width=f"{box['width']}px",
            height=f"{box['height'] + 2}px",
            print_background=True,
            page_ranges="1",
        )
        browser.close()


@dataclass
class Node:
    """知識体系マップの1つの枝。タグのない中間の枝（まとめるためだけの枝）は tag が None。"""

    tag: str | None
    label: str
    items: list[str]
    children: list["Node"] = field(default_factory=list)


def split_items(items: str) -> list[str]:
    """「apt／エディタ（nano／vim）」を、括弧の中では区切らずに「／」で分ける。"""
    result, depth, current = [], 0, ""
    for ch in items:
        depth += {"（": 1, "）": -1}.get(ch, 0)
        if ch == "／" and depth == 0:
            result.append(current)
            current = ""
        else:
            current += ch
    return [i for i in [*result, current] if i]


def knowledge_tree(text: str) -> list[Node]:
    """知識体系マップを木にする。返すのは大分野（tag なし、items は括弧内の説明）の一覧。"""
    body = _section(text, "### 知識体系マップ（木構造）")
    roots: list[Node] = []
    stack: list[Node] = []  # stack[d] が深さ d の直近の枝
    for line in body.splitlines():
        stripped = line.lstrip(" ")
        if not stripped.startswith("- "):
            continue
        depth = (len(line) - len(stripped)) // 4
        content = stripped[2:]
        if depth == 0:
            match = re.match(r"\*\*(.+?)\*\*（(.+)）", content)
            name, note = match.groups() if match else (content.strip("*"), "")
            node = Node(None, name, [note] if note else [])
            roots.append(node)
        else:
            match = re.match(r"`([^`]+)` (.+)", content)
            if match:
                tag, rest = match.groups()
                label, _, items = rest.partition("：")
                node = Node(tag, label, split_items(items))
            else:  # タグのない中間の枝
                node = Node(None, re.sub(r"（.*）$", "", content), [])
            stack[depth - 1].children.append(node)
        del stack[depth:]
        stack.append(node)
    return roots
