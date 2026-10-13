"""研修で扱う知識の系統図（知識体系マップ）を、スライド1枚の図にする。

- 知識体系マップの木を、根から枝分かれする横向きの系統図として描く。深さは決め打ちせず、
  マップに書いた階層のとおりに何段でも描く（同じ関数を再帰で使う）
- 一番下の枝には、マップの「：」の後ろにある内容（キーワード）を添える
- 向きは DIRECTION で切り替える（"ltr" は根が左で右へ広がる、"rtl" は根が右で左へ広がる）
- データは docs/curriculum.md の知識体系マップだけから取る（回との対応は全体像の図で示す）

出力: docs/diagrams/knowledge-map.html・.png・.pdf
使い方: python scripts/build_knowledge_map.py [--no-images]
"""

import html
import sys

from curriculum import read_curriculum
from overview import AREA_COLORS, FONT, FONT_LINK, INK, OUT_DIR, Node, export_images, knowledge_tree

GENERATED = "tools/scripts/build_knowledge_map.py で生成。手で編集しない"
DIRECTION = "ltr"
ROOT_LABEL = "全体"
e = html.escape


def render_node(node: Node, depth: int, color: tuple[str, str] | None) -> str:
    """1つの枝とその下の枝を描く。depth は根を 0 とした深さ。"""
    kind = "group" if node.tag is None and depth > 1 else f"d{min(depth, 3)}"
    style = f' style="--tint:{color[0]};--accent:{color[1]}"' if color and depth == 1 else ""
    tag = f"<code>{e(node.tag)}</code>" if node.tag else ""
    note = ""
    if node.items:
        if depth == 1:  # 大分野の括弧内の説明は、キーワードではなく補足として出す
            note = f'<div class="sub">{e(" ".join(node.items))}</div>'
        else:
            note = (
                '<div class="items">'
                + " / ".join(f"<span>{e(i)}</span>" for i in node.items)
                + "</div>"
            )
    leaf = " leaf" if not node.children and depth > 1 else ""  # 一番下の枝は名前とキーワードを1行に
    box = f'<div class="box {kind}{leaf}"><div class="label">{e(node.label)}{tag}</div>{note}</div>'
    if not node.children:
        return f'<div class="node"{style}>{box}</div>'
    children = []
    for i, child in enumerate(node.children):
        child_color = AREA_COLORS[i % len(AREA_COLORS)] if depth == 0 else color
        children.append(render_node(child, depth + 1, child_color))
    return f'<div class="node"{style}>{box}<div class="children">{"".join(children)}</div></div>'


def render_html(text: str) -> str:
    tree = render_node(Node(None, ROOT_LABEL, [], knowledge_tree(text)), 0, None)
    return f"""<!doctype html>
<!-- {GENERATED} -->
<html lang="ja"><head><meta charset="utf-8">
<title>研修で扱う知識の系統図</title>
{FONT_LINK}
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:#fff; color:{INK}; font-family:{FONT}; }}
.slide {{ display:inline-block; padding:32px 44px 28px; }}
header {{ display:flex; justify-content:space-between; align-items:baseline; gap:40px;
  border-bottom:2px solid {INK}; padding-bottom:8px; margin-bottom:20px; }}
h1 {{ font-size:22px; font-weight:700; }}
header p {{ font-size:11px; color:#666; }}
.tree {{ direction:{DIRECTION}; }}
.box {{ direction:ltr; }}
/* 枝: 箱の横に子の列を置き、線でつなぐ（向きは論理プロパティで direction に従う） */
.node {{ display:flex; align-items:center; }}
.children {{ display:flex; flex-direction:column; position:relative; padding-inline-start:22px; }}
.children::before {{ content:""; position:absolute; inset-inline-start:0; top:50%; width:22px; border-top:1px solid #8c8c8c; }}
.children > .node {{ position:relative; padding-inline-start:18px; padding-block:2px; }}
.children > .node::before {{ content:""; position:absolute; inset-inline-start:0; top:0; bottom:0; border-inline-start:1px solid #8c8c8c; }}
.children > .node:first-child::before {{ top:50%; }}
.children > .node:last-child::before {{ bottom:50%; }}
.children > .node:only-child::before {{ display:none; }}
.children > .node::after {{ content:""; position:absolute; inset-inline-start:0; top:50%; width:18px; border-top:1px solid #8c8c8c; }}
/* 箱: 深さごとに強さを変える */
.box {{ border:1px solid var(--accent,#8c8c8c); background:#fff; padding:4px 9px; border-radius:2px; max-width:340px; }}
.label {{ font-size:12px; font-weight:700; white-space:nowrap; }}
.sub {{ font-size:10.5px; color:#555; margin-top:2px; white-space:nowrap; }}
code {{ font:400 10.5px ui-monospace,Menlo,Consolas,monospace; color:#555; margin-inline-start:6px; }}
.items {{ font-size:10.5px; color:#555; line-height:1.45; margin-top:2px; }}
.items span {{ white-space:nowrap; }}
.d0 {{ border:1.5px solid {INK}; padding:8px 14px; }}
.d0 .label {{ font-size:15px; }}
.d1 {{ background:var(--tint); border:1.5px solid var(--accent); padding:7px 12px; }}
.d1 .label {{ font-size:15px; }}
.d2 {{ background:var(--tint); }}
.d2 .label {{ font-size:13px; }}
.leaf {{ display:flex; align-items:baseline; gap:10px; max-width:none; padding:3px 9px; }}
.leaf .items {{ margin-top:0; white-space:nowrap; }}
.group {{ border:1px dashed #8c8c8c; background:#fff; }}
.group .label {{ font-size:12px; color:#444; }}
footer {{ margin-top:16px; padding-top:6px; border-top:1px solid #bdbdbd; font-size:10.5px; color:#555; }}
</style></head>
<body><div class="slide">
<header><h1>研修で扱う知識の系統図</h1><p>出典: docs/curriculum.md の知識体系マップ</p></header>
<div class="tree">{tree}</div>
<footer>知識体系マップの枝分かれをそのまま描いた（深さは分野ごとに違う）。灰色の文字はタグ名で、各回の資料と Issue ラベルで共通に使う。</footer>
</div></body></html>
"""


def main(argv: list[str]) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "knowledge-map.html"
    out.write_text(render_html(read_curriculum()), encoding="utf-8")
    print("docs/diagrams/knowledge-map.html を生成しました")
    if "--no-images" not in argv:
        export_images(out)
        print("knowledge-map.png と knowledge-map.pdf を書き出しました")


if __name__ == "__main__":
    main(sys.argv[1:])
