"""タグ一覧とタグ索引を生成する。

- docs/tags.md                     タグ一覧（どの回で扱うか）
- docs/tags/<タグ名>/README.md     タグ索引
- docs/README.md の各回一覧（BEGIN sessions 〜 END sessions の間だけを書き換える）

カリキュラムでは「タグを資料のディレクトリ名にも使う」としている。資料本体は回ごとの
ディレクトリ（docs/sessionNN/）に置き、タグ名のディレクトリには索引だけを置く。
索引は各回の資料の冒頭（tag・前提タグ）とカリキュラムの副読本の表から作るので、手で編集しない。

使い方: python scripts/build_tag_index.py
"""

import shutil

from curriculum import (
    DOCS,
    Header,
    Session,
    knowledge_map_tags,
    parse_header,
    read_curriculum,
    readings,
    sessions,
    tag_ancestors,
    tag_matches,
)

TAGS_DIR = DOCS / "tags"
TAGS_MD = DOCS / "tags.md"
README = DOCS / "README.md"
BEGIN_SESSIONS = "<!-- BEGIN sessions"
END_SESSIONS = "<!-- END sessions -->"
GENERATED = "<!-- tools/scripts/build_tag_index.py で生成。手で編集しない -->"


def session_link(session: Session) -> str:
    return f"[第{session.number}回 {session.theme}](../../{session.dir_name}/README.md)"


def render(
    tag: str,
    description: str,
    known: set[str],
    headers: list[tuple[Session, Header]],
    text: str,
) -> str:
    ancestors = tag_ancestors(tag, known)
    children = [t for t in known if t != tag and tag in tag_ancestors(t, known)]
    lines = [
        f"# {tag}",
        "",
        GENERATED,
        "",
        description,
        "",
    ]
    if ancestors:
        lines.append("上位タグ: " + " → ".join(f"[{a}](../{a}/README.md)" for a in ancestors))
    if children:
        lines.append("下位タグ: " + ", ".join(f"[{c}](../{c}/README.md)" for c in sorted(children)))
    lines += ["", "## 扱う回", ""]

    def related(tags: tuple[str, ...]) -> list[str]:
        return [t for t in tags if tag_matches(tag, t)]

    direct = [(s, related(h.tags)) for s, h in headers if related(h.tags)]
    if direct:
        lines += [f"- {session_link(s)}（{', '.join(ts)}）" for s, ts in direct]
    else:
        lines.append("- どの回の tag にも入っていない（発展課題で触れる回はある）")

    prereq = [s for s, h in headers if related(h.prerequisites)]
    if prereq:
        lines += ["", "## 前提にしている回", ""]
        lines += [f"- {session_link(s)}" for s in prereq]

    books = [r for r in readings(text) if related(r.tags)]
    if books:
        lines += ["", "## 副読本・参考書・公式資料", ""]
        lines += [f"- [{r.title}]({r.url})：{r.usage}" for r in books]
    return "\n".join(lines) + "\n"


def sessions_for(tag: str, headers: list[tuple[Session, Header]]) -> str:
    numbers = [str(s.number) for s, h in headers if any(tag_matches(tag, t) for t in h.tags)]
    return ", ".join(numbers) if numbers else "—"


def render_tags_md(tags: dict[str, str], headers: list[tuple[Session, Header]]) -> str:
    lines = [
        "# タグ一覧",
        "",
        GENERATED,
        "",
        "知識体系マップ（[curriculum.md](curriculum.md#知識体系マップ木構造)）のタグを並べたものです。",
        "同じタグ名を、資料の冒頭と Issue ラベルで共通に使います。",
        "タグ名のリンク先は、そのタグを扱う回と副読本をまとめた索引です。",
        "",
        "| タグ | 内容 | 扱う回 |",
        "| --- | --- | --- |",
    ]
    for tag, description in tags.items():
        lines.append(
            f"| [{tag}](tags/{tag}/README.md) | {description} | {sessions_for(tag, headers)} |"
        )
    return "\n".join(lines) + "\n"


def render_session_table(headers: list[tuple[Session, Header]]) -> str:
    lines = [
        "| 回 | テーマ | 所要 | tag | 前提タグ | 成果物 | 資料 | 見本 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for s, h in headers:
        d = s.dir_name
        lines.append(
            f"| 第{s.number}回 | {s.theme} | {s.duration} | {', '.join(s.tags)} | "
            f"{', '.join(h.prerequisites) or 'なし'} | {s.deliverable} | "
            f"[{d}]({d}/README.md) | [{d}](../examples/{d}/README.md) |"
        )
    return "\n".join(lines)


def replace_between_markers(text: str, body: str) -> str:
    start = text.index(BEGIN_SESSIONS)
    start = text.index("\n", start) + 1
    end = text.index(END_SESSIONS)
    return text[:start] + body + "\n" + text[end:]


def main() -> None:
    text = read_curriculum()
    tags = knowledge_map_tags(text)
    known = set(tags)
    headers = []
    for session in sessions(text):
        path = DOCS / session.dir_name / "README.md"
        if path.exists():
            headers.append((session, parse_header(path)))

    if TAGS_DIR.exists():
        shutil.rmtree(TAGS_DIR)
    for tag, description in tags.items():
        out = TAGS_DIR / tag / "README.md"
        out.parent.mkdir(parents=True)
        out.write_text(render(tag, description, known, headers, text), encoding="utf-8")
    README.write_text(
        replace_between_markers(README.read_text(encoding="utf-8"), render_session_table(headers)),
        encoding="utf-8",
    )
    TAGS_MD.write_text(render_tags_md(tags, headers), encoding="utf-8")
    print(f"{len(tags)} 個のタグについて、タグ一覧とタグ索引を生成しました")


if __name__ == "__main__":
    main()
