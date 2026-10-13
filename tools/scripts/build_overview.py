"""研修の全体像を、スライド1枚のようなブロック配置の図にする（HTML 版と Mermaid 版）。

- 列はフェーズと回、行（レーン）は大分野。ジャンルは扱う最初の回から最後の回までの横棒で置く
- 前提関係は矢印ではなく「左にあるものが先」という位置で示す
- 下に横断テーマを、始まる回から最終回までの帯で示す
- データは docs/curriculum.md と各回の資料の冒頭から取る（overview.py）

HTML 版は Playwright（Chromium）で PNG と PDF に書き出す。Mermaid 版（block-beta）は同じ配置を
Markdown の中でも見られるようにしたもので、画像にするのは mise の diagrams タスク（mermaid-cli）。
出力: docs/diagrams/overview.html・.png・.pdf、overview.mmd
使い方: python scripts/build_overview.py [--no-images]
"""

import html
import sys

from curriculum import read_curriculum, sessions
from overview import (
    AREA_COLORS,
    FONT,
    FONT_LINK,
    INK,
    OUT_DIR,
    analyze,
    export_images,
    pack,
    phases,
    session_list,
    themes,
)

GENERATED = "tools/scripts/build_overview.py で生成。手で編集しない"
COL = 124  # 1回分の列の幅（px）
LABEL = 168  # レーン名の列の幅（px）


def render_html(text: str) -> str:
    known = analyze(text)
    all_sessions = sessions(text)
    count = len(all_sessions)
    areas = list(dict.fromkeys(g.area for g in known.values()))
    colors = dict(zip(areas, AREA_COLORS, strict=False))
    e = html.escape

    cells = ['<div class="corner"></div>']
    for name, first, last in phases(text):
        cells.append(
            f'<div class="phase" style="grid-column:{first + 1}/{last + 2}">{e(name)}</div>'
        )
    for s in all_sessions:
        cells.append(
            f'<div class="session" style="grid-column:{s.number + 1}">'
            f"<b>第{s.number}回</b><span>{e(s.theme)}</span></div>"
        )

    for area in areas:
        tint, accent = colors[area]
        bars = []
        for g, row in pack([g for g in known.values() if g.area == area and g.sessions]):
            first, last = g.span
            marks = "".join(
                f'<i style="grid-column:{n - first + 1}"></i>' for n in sorted(g.sessions)
            )
            bars.append(
                f'<div class="bar" style="grid-column:{first}/{last + 1};grid-row:{row}">'
                f'<div class="name">{e(g.label)} <code>{e(g.tag)}</code></div>'
                f'<div class="marks" style="grid-template-columns:repeat({last - first + 1},1fr)">'
                f"{marks}</div></div>"
            )
        cells.append(
            f'<section class="lane" style="--tint:{tint};--accent:{accent}">'
            f'<h2>{e(area)}</h2><div class="track">{"".join(bars)}</div></section>'
        )

    bands = "".join(
        f'<div class="band" style="grid-column:{t.start}/{count + 1};grid-row:{i + 1}">'
        f"{e(t.name)}<small>第{t.start}回〜</small></div>"
        for i, t in enumerate(themes(text))
    )
    cells.append(
        f'<section class="lane themes"><h2>横断テーマ</h2><div class="track">{bands}</div></section>'
    )

    return f"""<!doctype html>
<!-- {GENERATED} -->
<html lang="ja"><head><meta charset="utf-8">
<title>研修の全体像</title>
{FONT_LINK}
<style>
* {{ box-sizing:border-box; margin:0; }}
body {{ background:#fff; color:{INK}; font-family:{FONT}; }}
.slide {{ width:{LABEL + COL * count + 88}px; padding:32px 44px 28px; }}
header {{ display:flex; justify-content:space-between; align-items:baseline;
  border-bottom:2px solid {INK}; padding-bottom:8px; margin-bottom:18px; }}
h1 {{ font-size:22px; font-weight:700; }}
header p {{ font-size:11px; color:#666; }}
.board {{ display:grid; grid-template-columns:{LABEL}px repeat({count},{COL}px); }}
.phase {{ border-top:3px solid {INK}; margin-right:8px; padding:4px 2px 0; font-size:12px; font-weight:700; }}
.session {{ grid-row:2; padding:6px 6px 10px; border-left:1px solid #d6d6d6; }}
.session b {{ display:block; font-size:12px; }}
.session span {{ display:block; font-size:10.5px; color:#555; line-height:1.4; margin-top:1px; }}
.lane {{ grid-column:1/-1; display:grid; grid-template-columns:subgrid; border-top:1px solid #bdbdbd; padding:10px 0; }}
.lane h2 {{ grid-column:1; font-size:13px; font-weight:700; padding-right:12px; }}
.lane h2::before {{ content:""; display:inline-block; width:10px; height:10px; margin-right:6px;
  background:var(--accent,{INK}); vertical-align:-1px; }}
.track {{ grid-column:2/-1; display:grid; grid-template-columns:subgrid; row-gap:6px;
  background-image:repeating-linear-gradient(90deg,#e4e4e4 0 1px,transparent 1px {COL}px); }}
.bar {{ background:var(--tint); border:1px solid var(--accent); border-radius:2px;
  margin:0 4px; padding:5px 8px 5px; }}
.name {{ font-size:12.5px; font-weight:700; line-height:1.35; }}
.name code {{ display:inline-block; white-space:nowrap; font:400 10.5px ui-monospace,Menlo,Consolas,monospace; color:#555; }}
.marks {{ display:grid; margin:5px -8px 0; }}
.marks i {{ justify-self:center; width:7px; height:7px; background:var(--accent); }}
.themes .track {{ row-gap:4px; }}
.band {{ margin:0 4px; padding:3px 8px; background:#eeeeee; border-left:3px solid {INK}; font-size:12px; font-weight:700; }}
.band small {{ font-weight:400; color:#555; margin-left:8px; }}
footer {{ margin-top:12px; padding-top:6px; border-top:1px solid #bdbdbd; font-size:10.5px; color:#555; }}
</style></head>
<body><div class="slide">
<header><h1>1年目エンジニア研修の全体像（全{count}回）</h1><p>出典: docs/curriculum.md、各回の資料の冒頭</p></header>
<div class="board">
{chr(10).join(cells)}
</div>
<footer>■ はそのジャンルを扱う回。横棒は扱う最初の回から最後の回まで。左にあるジャンルが、右の回の前提になる。</footer>
</div></body></html>
"""


def render_mermaid(text: str) -> str:
    """HTML 版と同じ配置を Mermaid の block-beta で書く（1列目はレーン名、2列目以降が各回）。"""
    known = analyze(text)
    count = len(sessions(text))
    areas = list(dict.fromkeys(g.area for g in known.values()))
    lines = [
        f"%% {GENERATED}",
        "%%{init: {'theme': 'base', 'themeVariables': {'fontFamily': 'BIZ UDPGothic, sans-serif',"
        f" 'fontSize': '15px', 'primaryTextColor': '{INK}'}}}}%%",
        "block-beta",
        f"  columns {count + 1}",
    ]

    def row(label: str, label_id: str, items: list[tuple[int, int, str]]) -> str:
        """items は (最初の回, 最後の回, ブロックの書き方) で、回の順に並んでいること。"""
        parts = [f'{label_id}["{label}"]' if label else "space"]
        cursor = 1
        for first, last, block in items:
            if first > cursor:
                parts.append(f"space:{first - cursor}" if first - cursor > 1 else "space")
            parts.append(f"{block}:{last - first + 1}" if last > first else block)
            cursor = last + 1
        if cursor <= count:
            parts.append(f"space:{count - cursor + 1}" if count - cursor > 0 else "space")
        return "  " + " ".join(parts)

    lines.append(row("", "", [(f, last, f'p{f}["{name}"]') for name, f, last in phases(text)]))
    lines.append(
        row(
            "", "", [(s.number, s.number, f's{s.number}["第{s.number}回"]') for s in sessions(text)]
        )
    )
    classes: dict[str, list[str]] = {}
    for i, area in enumerate(areas):
        placed = pack([g for g in known.values() if g.area == area and g.sessions])
        for r in range(1, max((r for _, r in placed), default=0) + 1):
            items = []
            for g, gr in placed:
                if gr == r:
                    first, last = g.span
                    gid = f"g{list(known).index(g.tag)}"  # 日本語の ID は class 指定が効かない
                    label = f"<b>{g.label}</b><br/>{g.tag}・第{session_list(g.sessions)}回"
                    items.append((first, last, f'{gid}["{label}"]'))
                    classes.setdefault(f"area{i}", []).append(gid)
            lines.append(row(area if r == 1 else "", f"lane{i}", sorted(items)))
            if r == 1:
                classes.setdefault("lane", []).append(f"lane{i}")
    for i, t in enumerate(themes(text)):
        label_id = "themes" if i == 0 else ""
        lines.append(
            row(
                "横断テーマ" if i == 0 else "",
                label_id,
                [(t.start, count, f't{i}["{t.name}　第{t.start}回〜"]')],
            )
        )
        classes.setdefault("theme", []).append(f"t{i}")
    classes["lane"].append("themes")
    classes["phase"] = [f"p{f}" for _, f, _ in phases(text)]
    classes["session"] = [f"s{s.number}" for s in sessions(text)]

    for i, (tint, accent) in enumerate(AREA_COLORS[: len(areas)]):
        lines.append(f"  classDef area{i} fill:{tint},stroke:{accent},color:{INK}")
    lines += [
        "  classDef lane fill:#ffffff,stroke:#ffffff,color:" + INK,
        f"  classDef phase fill:#ffffff,stroke:{INK},stroke-width:2px,color:{INK}",
        "  classDef session fill:#ffffff,stroke:#d6d6d6,color:#333333",
        f"  classDef theme fill:#eeeeee,stroke:#eeeeee,color:{INK}",
    ]
    lines += [f"  class {','.join(ids)} {name}" for name, ids in classes.items()]
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    text = read_curriculum()
    (OUT_DIR / "overview.mmd").write_text(render_mermaid(text), encoding="utf-8")
    out = OUT_DIR / "overview.html"
    out.write_text(render_html(text), encoding="utf-8")
    print("docs/diagrams/overview.html と overview.mmd を生成しました")
    if "--no-images" not in argv:
        export_images(out)
        print("overview.png と overview.pdf を書き出しました")


if __name__ == "__main__":
    main(sys.argv[1:])
