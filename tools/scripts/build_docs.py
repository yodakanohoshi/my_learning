"""docs/ の Markdown を、Vivliostyle で HTML 版と PDF 版（全部を1冊）にする。

- 対象は docs/ 以下の .md。講師用（instructor.md）と _ で始まるディレクトリ（_template/、_build/）は
  除く
- HTML 版: 資料どうしのリンクは .html に、docs/ の外（examples/ など）へのリンクは元のファイルへの
  相対パスに書き換える。コードブロックにはコピーボタン、各ページの下には目次・全体概要・タグ一覧と
  「戻る」のナビを付ける（tools/docs_theme/）
- PDF 版: HTML 版と同じページを1冊にまとめる。資料どうしのリンクは PDF の中のページジャンプになり、
  各ページの下の余白にナビ（目次・全体概要・タグ一覧）を出す。PDF の外へのリンクは PDF からの
  相対パス
- Mermaid のコードブロックは mermaid-cli で SVG にしてページに埋め込む（HTML 版と PDF 版で同じ図。
  見た目は tools/docs_theme/mermaid.json）
- PlantUML のコードブロックも同じように SVG にする（Java が要る。PlantUML の jar は初回に
  Maven Central から tools/.cache/ に取ってくる。見た目は tools/docs_theme/plantuml.puml）
- 描画には Playwright の Chromium を使う（Vivliostyle が自分で入れる Chromium は、環境によって
  入らないため）

出力: docs/_build/html/（入口は index.html の目次）、docs/_build/handsoff.pdf
使い方: python scripts/build_docs.py [--no-pdf]
"""

import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote, unquote

from curriculum import DOCS, ROOT

VIVLIOSTYLE = "@vivliostyle/cli@9.9.0"
MERMAID_CLI = "@mermaid-js/mermaid-cli@11.4.2"
PLANTUML_VERSION = "1.2026.7"
PLANTUML_JAR = ROOT / "tools" / ".cache" / f"plantuml-{PLANTUML_VERSION}.jar"
PLANTUML_URL = (
    "https://repo1.maven.org/maven2/net/sourceforge/plantuml/plantuml/"
    f"{PLANTUML_VERSION}/plantuml-{PLANTUML_VERSION}.jar"
)
THEME = ROOT / "tools" / "docs_theme"
OUT = DOCS / "_build"
PDF_NAME = "handsoff.pdf"
TITLE = "1年目エンジニア研修 資料"
TOC = "index.html"
# 各ページの下のナビ（表示名, docs/ からのパス）
NAV = [("目次", TOC), ("全体概要", "README.html"), ("タグ一覧", "tags.html")]
# 先頭のディレクトリ・ファイルの並び。ここにないものは後ろに名前順で並べる
TOP_ORDER = ["README.md", "curriculum.md", "session", "tags.md", "tags", "templates"]

ATTR = re.compile(r'\b(href|src)="([^"]*)"')
SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
SHELL_BLOCK = re.compile(r'(<code class="language-(?:sh|bash|shell)">)(.*?)(</code>)', re.S)
SHELL_LINE = re.compile(r"^(\s*)([^\s#;|&<>]+)(.*?)((?:(?<=\s)|^)#.*)?$")
PLANTUML = re.compile(
    r'<pre class="language-plantuml"><code class="language-plantuml">(.*?)</code></pre>', re.S
)
MERMAID = re.compile(
    r'<pre class="language-mermaid"><code class="language-mermaid">(.*?)</code></pre>', re.S
)


def sort_key(rel: Path) -> tuple[int, list[tuple[int, str]]]:
    """全体概要 → カリキュラム → 各回 → タグ → テンプレート → その他の順に並べる。

    どのディレクトリも README.md が先。ここにないものは後ろに名前順で並べる。
    """
    top = rel.parts[0]
    rank = next(
        (i for i, name in enumerate(TOP_ORDER) if top == name or top.startswith(name)),
        len(TOP_ORDER),
    )
    return rank, [(0 if p == "README.md" else 1, p) for p in rel.parts]


def collect_entries() -> list[Path]:
    """docs/ からの相対パスで、PDF に載せる順に並べた Markdown。"""
    entries = [
        p.relative_to(DOCS)
        for p in DOCS.rglob("*.md")
        if p.name != "instructor.md"
        and not any(s.startswith("_") for s in p.relative_to(DOCS).parts)
    ]
    return sorted(entries, key=sort_key)


def relative_href(target: Path, start: Path) -> str:
    return quote(Path(os.path.relpath(target, start)).as_posix())


def rewrite_link(value: str, page: Path, root: Path, entries: set[Path], *, for_pdf: bool) -> str:
    """page（root からの相対パスの .html）にあるリンク・画像のパスを書き換える。"""
    if not value or value.startswith("#") or SCHEME.match(value) or value.startswith("//"):
        return value
    path, sep, fragment = value.partition("#")
    target = Path(os.path.normpath(DOCS / page.parent / unquote(path)))
    if target.is_dir():
        target = target / "README.md"
    rel = Path(os.path.relpath(target, DOCS))
    md = rel.with_suffix(".md")
    if rel.parts[0] != ".." and md in entries and rel.suffix in (".md", ".html"):
        new = relative_href(root / md.with_suffix(".html"), root / page.parent)
    elif (root / rel).exists() or rel == Path(TOC):
        return value  # Vivliostyle が出力にコピーした画像など
    elif for_pdf:
        new = target.as_uri()  # PDF を作った後で、PDF からの相対パスに直す
    else:
        new = relative_href(target, root / page.parent)
    return new + sep + fragment


def decorate(text: str, page: Path, root: Path, entries: set[Path], *, for_pdf: bool) -> str:
    """リンクを書き換え、テーマ・スクリプト・ナビを入れる。"""
    text = ATTR.sub(
        lambda m: (
            f'{m[1]}="{rewrite_link(html.unescape(m[2]), page, root, entries, for_pdf=for_pdf)}"'
        ),
        text,
    )
    up = "../" * (len(page.parts) - 1)
    head = f'<link rel="stylesheet" href="{up}theme.css">'
    if not for_pdf:
        head += f'\n<script src="{up}docs.js" defer></script>'
    links = "".join(f'<a href="{up}{quote(href)}">{name}</a>' for name, href in NAV)
    text = text.replace("</head>", f"{head}\n</head>", 1)
    return re.sub(
        r"<body([^>]*)>", rf'<body\1>\n<nav class="page-nav">{links}</nav>', text, count=1
    )


def chromium() -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        return p.chromium.executable_path


def vivliostyle(config: dict[str, object], workdir: Path) -> None:
    path = workdir / "vivliostyle.config.js"
    path.write_text(f"module.exports = {json.dumps(config, ensure_ascii=False, indent=2)};\n")
    cmd = ["npx", "-y", VIVLIOSTYLE, "build", "-c", str(path), "--executable-browser", chromium()]
    subprocess.run(cmd, check=True, cwd=workdir)


def render_mermaid(raw: Path, workdir: Path) -> None:
    """raw の各ページの Mermaid のコードブロックを、SVG の図に置き換える。

    mermaid-cli の Markdown 入力を使い、全ページの図を1回の起動でまとめて描く。
    """
    pages = sorted(raw.rglob("*.html"))
    sources = [
        html.unescape(re.sub(r"<[^>]+>", "", m[1]))
        for page in pages
        for m in MERMAID.finditer(page.read_text())
    ]
    if not sources:
        return
    out = workdir / "mermaid"
    out.mkdir()
    blocks = "".join(f"```mermaid\n{s.strip()}\n```\n\n" for s in sources)
    (out / "in.md").write_text(blocks)
    puppeteer = out / "puppeteer.json"
    puppeteer.write_text(json.dumps({"args": ["--no-sandbox"], "executablePath": chromium()}))
    cmd = [
        "npx", "-y", MERMAID_CLI, "-p", str(puppeteer), "-c", str(THEME / "mermaid.json"),
        "-C", str(ROOT / "tools" / "mermaid.css"),  # ページと同じフォントで文字幅を測る
        "-i", "in.md", "-o", "out.md", "-e", "svg", "-b", "transparent",
    ]  # fmt: skip
    subprocess.run(cmd, check=True, cwd=out, stdout=subprocess.DEVNULL)
    count = iter(range(1, len(sources) + 1))

    def figure(_: re.Match[str]) -> str:
        n = next(count)
        svg = (out / f"out-{n}.svg").read_text().replace("my-svg", f"mermaid-{n}")
        return f'<figure class="mermaid">{svg}</figure>'

    for page in pages:
        text = page.read_text()
        if MERMAID.search(text):
            page.write_text(MERMAID.sub(figure, text))


def highlight_shell_line(line: str) -> str:
    """シェルの1行の、先頭のコマンド名と # 以降のコメントに色の目印を付ける。"""
    stripped = line.lstrip()
    if stripped.startswith("#"):  # 行全体がコメント
        return f'{line[: len(line) - len(stripped)]}<span class="token comment">{stripped}</span>'
    m = SHELL_LINE.match(line)
    if not m:
        return line
    indent, command, rest, comment = m[1], m[2], m[3], m[4] or ""
    out = f'{indent}<span class="token function">{command}</span>{rest}'
    return out + (f'<span class="token comment">{comment}</span>' if comment else "")


def highlight_shell(raw: Path) -> None:
    """VFM が色を付けない sh のコードブロックに、コマンド名とコメントの色の目印を付ける。"""
    for page in raw.rglob("*.html"):
        text = page.read_text()
        if "language-sh" not in text and "language-bash" not in text:
            continue

        def block(m: re.Match[str]) -> str:
            if "<span" in m[2]:  # すでに色が付いている
                return m[0]
            lines = m[2].split("\n")
            return m[1] + "\n".join(highlight_shell_line(line) for line in lines) + m[3]

        page.write_text(SHELL_BLOCK.sub(block, text))


def plantuml_jar() -> Path:
    """PlantUML の jar。なければ Maven Central から取ってくる。"""
    if not PLANTUML_JAR.exists():
        import urllib.request

        PLANTUML_JAR.parent.mkdir(parents=True, exist_ok=True)
        print(f"PlantUML {PLANTUML_VERSION} を取ってきます")
        urllib.request.urlretrieve(PLANTUML_URL, PLANTUML_JAR)
    return PLANTUML_JAR


def plantuml_source(code: str) -> str:
    """コードブロックの中身を、テーマを読み込んだ PlantUML の図にする。"""
    lines = code.strip().splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip().startswith("@start")), None)
    include = f"!include {THEME / 'plantuml.puml'}"
    if start is None:  # @startuml を省いた書き方
        return "\n".join(["@startuml", include, *lines, "@enduml"]) + "\n"
    return "\n".join([*lines[: start + 1], include, *lines[start + 1 :]]) + "\n"


def render_plantuml(raw: Path, workdir: Path) -> None:
    """raw の各ページの PlantUML のコードブロックを、SVG の図に置き換える。"""
    pages = sorted(raw.rglob("*.html"))
    sources = [
        html.unescape(re.sub(r"<[^>]+>", "", m[1]))
        for page in pages
        for m in PLANTUML.finditer(page.read_text())
    ]
    if not sources:
        return
    out = workdir / "plantuml"
    out.mkdir()
    for n, source in enumerate(sources, 1):
        (out / f"{n}.puml").write_text(plantuml_source(source))
    cmd = ["java", "-jar", str(plantuml_jar()), "-tsvg", "-charset", "UTF-8", "-failfast2"]
    subprocess.run([*cmd, *(f"{n}.puml" for n in range(1, len(sources) + 1))], check=True, cwd=out)
    count = iter(range(1, len(sources) + 1))

    def figure(_: re.Match[str]) -> str:
        svg = (out / f"{next(count)}.svg").read_text()
        svg = svg[svg.index("<svg") :]  # 先頭の XML 宣言を外す
        # PlantUML はフォントの並びを1つの名前として引用符で囲むので、並びとして読める形に戻す
        svg = re.sub(r"font-family=\"'([^']*)'\"", r'font-family="\1"', svg)
        return f'<figure class="plantuml">{svg}</figure>'

    for page in pages:
        text = page.read_text()
        if PLANTUML.search(text):
            page.write_text(PLANTUML.sub(figure, text))


def build_html(entries: list[Path], workdir: Path) -> Path:
    """Markdown を HTML にし（目次 index.html を足す）、出力先 workdir/raw を返す。"""
    raw = workdir / "raw"
    config: dict[str, object] = {
        "title": TITLE,
        "language": "ja",
        "entryContext": str(DOCS),
        "entry": [e.as_posix() for e in entries],
        "vfm": {"hardLineBreaks": True},
        # docs/ の画像などは出力にコピーされる。前回の出力（_build）まで
        # 入れ子でコピーしないように外す
        "copyAsset": {"excludes": ["_build/**", "_template/**"]},
        "output": [{"path": str(raw), "format": "webpub"}],
    }
    vivliostyle(config, workdir)
    (raw / "publication.json").unlink(missing_ok=True)
    render_mermaid(raw, workdir)
    render_plantuml(raw, workdir)
    highlight_shell(raw)
    (raw / TOC).write_text(render_toc(entries, raw))
    return raw


def toc_parent(entry: Path, entries: set[Path]) -> Path | None:
    """目次で entry をぶら下げるページ。近いディレクトリから順に、README.md か
    <ディレクトリ名>.md を探す。

    docs/README.md（全体概要）はぶら下げ先にしない。見つからなければ None（目次の1段目）。
    """
    d = entry.parent.parent if entry.name == "README.md" else entry.parent
    while d != Path("."):
        for candidate in (d / "README.md", d.parent / f"{d.name}.md"):
            if candidate != entry and candidate in entries:
                return candidate
        d = d.parent
    return None


def page_title(file: Path) -> str:
    """ページの h1。h1 のないページ（テンプレートなど）はファイル名。"""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", file.read_text(), re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m[1])).strip() if m else file.stem


def render_toc(entries: list[Path], raw: Path) -> str:
    """目次。子のページ（タグ・テンプレート・各回の付録）は親の下に小さく横に並べる。"""
    entry_set = set(entries)
    children: dict[Path | None, list[Path]] = {}
    for e in entries:
        children.setdefault(toc_parent(e, entry_set), []).append(e)

    def item(e: Path) -> str:
        page = e.with_suffix(".html")
        link = f'<a href="{quote(page.as_posix())}">{html.escape(page_title(raw / page))}</a>'
        sub = "".join(item(c) for c in children.get(e, []))
        return f"<li>{link}{f'<ol>{sub}</ol>' if sub else ''}</li>"

    items = "".join(item(e) for e in children.get(None, []))
    return (
        f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>{TITLE}</title>'
        '<meta name="viewport" content="width=device-width, initial-scale=1"></head><body>'
        f'<h1>{TITLE}</h1><nav id="toc" role="doc-toc"><h2>目次</h2><ol>{items}</ol></nav>'
        "</body></html>\n"
    )


def write_site(raw: Path, dest: Path, entries: set[Path], *, for_pdf: bool) -> list[Path]:
    """raw を dest にコピーして各ページを仕上げ、ページ（dest からの相対パス）を返す。"""
    shutil.copytree(raw, dest)
    for name in ("theme.css", "docs.js"):
        shutil.copy2(THEME / name, dest / name)
    pages = sorted(p.relative_to(dest) for p in dest.rglob("*.html"))
    for page in pages:
        file = dest / page
        file.write_text(decorate(file.read_text(), page, dest, entries, for_pdf=for_pdf))
    return pages


def fix_pdf_links(pdf: Path) -> None:
    """PDF の外のファイルへのリンク（file://）を、PDF からの相対パスにする。"""
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import NameObject, TextStringObject

    writer = PdfWriter(clone_from=PdfReader(pdf))
    for page in writer.pages:
        for annot in page.get("/Annots") or []:
            action = annot.get_object().get("/A")
            uri = action.get("/URI") if action else None
            if isinstance(uri, str) and uri.startswith("file://"):
                target = Path(unquote(uri.removeprefix("file://")))
                action[NameObject("/URI")] = TextStringObject(
                    Path(os.path.relpath(target, pdf.parent)).as_posix()
                )
    writer.write(pdf)


def main(argv: list[str]) -> int:
    with_pdf = "--no-pdf" not in argv
    entries = collect_entries()
    entry_set = set(entries)
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        raw = build_html(entries, work)
        shutil.rmtree(OUT / "html", ignore_errors=True)  # --no-pdf のときは前回の PDF を残す
        OUT.mkdir(parents=True, exist_ok=True)
        write_site(raw, OUT / "html", entry_set, for_pdf=False)
        print(f"HTML: {(OUT / 'html' / TOC).relative_to(ROOT)}")
        if with_pdf:
            pdf_site = work / "pdf"
            write_site(raw, pdf_site, entry_set, for_pdf=True)
            pdf = OUT / PDF_NAME
            order = [Path(TOC)] + [e.with_suffix(".html") for e in entries]
            config: dict[str, object] = {
                "title": TITLE,
                "language": "ja",
                "entryContext": str(pdf_site),
                "entry": [p.as_posix() for p in order],
                "output": [{"path": str(pdf), "format": "pdf"}],
                # 図（SVG）が多く、既定の5分では描き終わらないので延ばす
                "timeout": 30 * 60 * 1000,
            }
            vivliostyle(config, work)
            fix_pdf_links(pdf)
            print(f"PDF: {pdf.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
