import build_overview
import overview
from curriculum import read_curriculum


def test_横断テーマは始まる回とともに読み取る() -> None:
    themes = {t.name: t.start for t in overview.themes(read_curriculum())}
    assert themes == {"Git": 5, "ドキュメント": 9, "環境の再現性": 4, "TDD": 8}


def test_同じ行の横棒は重ならない() -> None:
    known = overview.analyze(read_curriculum())
    for area in {g.area for g in known.values()}:
        placed = overview.pack([g for g in known.values() if g.area == area and g.sessions])
        rows: dict[int, list[tuple[int, int]]] = {}
        for g, row in placed:
            rows.setdefault(row, []).append((min(g.sessions), max(g.sessions)))
        for spans in rows.values():
            spans.sort()
            assert all(a[1] < b[0] for a, b in zip(spans, spans[1:], strict=False))


def test_HTML_には全回とジャンルが入る() -> None:
    text = build_overview.render_html(read_curriculum())
    assert "第12回" in text and "画面の部分更新と成果発表" in text
    assert "バージョン管理（Git）" in text


def test_ジャンルは大分野の1つ下の枝_タグのない枝はさらに1つ下() -> None:
    genres = overview.genres(read_curriculum())
    assert genres["linux"].area == "コンピュータ基盤"
    assert {"git", "env", "標準", "pm"} <= set(genres)
    assert "linux-ファイル" not in genres
    assert overview.genre_of("http-基本", genres) == "http"


def test_Mermaid版は各行の列数が全体の列数と同じ() -> None:
    import re

    text = build_overview.render_mermaid(read_curriculum())
    columns = int(re.search(r"columns (\d+)", text).group(1))  # type: ignore[union-attr]
    for line in text.splitlines():
        if line.startswith("  ") and ("[" in line or "space" in line) and "classDef" not in line:
            if line.strip().startswith(("class ", "columns")):
                continue
            width = 0
            for part in re.findall(r'(?:\w+\["[^"]*"\]|space)(?::(\d+))?', line):
                width += int(part) if part else 1
            assert width == columns, line


def test_系統図の木は大分野からタグの深さまでたどれる() -> None:
    roots = overview.knowledge_tree(read_curriculum())
    assert [r.label for r in roots] == [
        "コンピュータ基盤",
        "実装技術",
        "ソフトウェア開発",
        "その他",
    ]
    pm = next(c for c in roots[3].children if c.tag == "pm")
    assert [c.tag for c in pm.children] == ["pm-見積", "pm-進捗"]
    http = next(c for c in roots[0].children if c.tag == "http")
    assert [c.tag for c in http.children] == [
        "http-基本",
        "http-ブラウザ",
        "http-構成",
        "http-リアルタイム",
    ]
    linux = next(c for c in roots[0].children if c.tag == "linux")
    assert "linux-ネットワーク" in [c.tag for c in linux.children]
    assert {"git", "env", "標準"} <= {c.tag for c in roots[2].children}


def test_項目は括弧の中では区切らない() -> None:
    assert overview.split_items("apt／エディタ（nano／vim）／ps") == [
        "apt",
        "エディタ（nano／vim）",
        "ps",
    ]


def test_系統図は回を書かず_マップの深さのとおりに入れ子にする() -> None:
    import build_knowledge_map

    text = build_knowledge_map.render_html(read_curriculum())
    assert "第1回" not in text
    # 根 → コンピュータ基盤 → ネットワーク → Web通信 → HTTPの基本 の5段
    assert text.count('<div class="children">') >= 4
    assert "http-基本" in text and "box d3 leaf" in text
