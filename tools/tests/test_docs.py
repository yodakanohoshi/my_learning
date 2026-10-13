from pathlib import Path

import build_docs
from curriculum import DOCS, ROOT

ENTRIES = set(build_docs.collect_entries())


def test_講師用とアンダースコアのディレクトリは載せない() -> None:
    assert not any(e.name == "instructor.md" for e in ENTRIES)
    assert not any(e.parts[0].startswith("_") for e in ENTRIES)


def test_全体概要_カリキュラム_各回_タグ_テンプレートの順() -> None:
    order = [e.as_posix() for e in build_docs.collect_entries()]
    assert order[:3] == ["README.md", "curriculum.md", "session01/README.md"]
    assert (
        order.index("session12/README.md")
        < order.index("tags.md")
        < order.index("templates/README.md")
    )
    assert order.index("templates/README.md") < order.index("templates/api-design.md")


def rewrite(value: str, page: str, *, for_pdf: bool = False) -> str:
    root = DOCS / "_build" / "html"
    return build_docs.rewrite_link(value, Path(page), root, ENTRIES, for_pdf=for_pdf)


def test_資料どうしのリンクは_html_にする() -> None:
    assert rewrite("../tags.md", "session01/README.html") == "../tags.html"
    assert rewrite("../session06/README.md#宿題必須課題", "session05/README.html") == (
        "../session06/README.html#宿題必須課題"
    )


def test_外へのリンクは元のファイルへ_PDF_は絶対パスにしておく() -> None:
    target = ROOT / "examples" / "session04" / "README.md"
    assert rewrite("../../examples/session04/README.md", "session04/README.html") == (
        "../../../../examples/session04/README.md"
    )
    assert rewrite("../../examples/session04/README.md", "session04/README.html", for_pdf=True) == (
        target.as_uri()
    )


def test_外部の_URL_とページ内のリンクはそのまま() -> None:
    for value in ["https://example.com/", "#ゴール", "mailto:a@example.com"]:
        assert rewrite(value, "session01/README.html") == value


def test_PDF_版にはスクリプトを入れず_ナビは入れる() -> None:
    text = '<html><head></head><body class="x"><p>a</p></body></html>'
    page = Path("session01/README.html")
    root = DOCS / "_build" / "html"
    pdf = build_docs.decorate(text, page, root, ENTRIES, for_pdf=True)
    site = build_docs.decorate(text, page, root, ENTRIES, for_pdf=False)
    assert "docs.js" not in pdf and '<script src="../docs.js"' in site
    assert '<body class="x">\n<nav class="page-nav"><a href="../index.html">目次</a>' in pdf


def test_目次ではタグ_テンプレート_付録を親の下に入れる() -> None:
    parent = {e.as_posix(): build_docs.toc_parent(e, ENTRIES) for e in ENTRIES}
    assert parent["tags/db/README.md"] == Path("tags.md")
    assert parent["templates/api-design.md"] == Path("templates/README.md")
    assert parent["session05/assets/commit-convention.md"] == Path("session05/README.md")
    for top in [
        "README.md",
        "curriculum.md",
        "session01/README.md",
        "tags.md",
        "templates/README.md",
    ]:
        assert parent[top] is None


def test_sh_のコードブロックはコマンド名とコメントに色を付ける() -> None:
    h = build_docs.highlight_shell_line
    command = '<span class="token function">ps</span>'
    comment = '<span class="token comment"># PPID を見る</span>'
    assert h("ps -f   # PPID を見る") == f"{command} -f   {comment}"
    assert h("  # 行全体") == '  <span class="token comment"># 行全体</span>'
    assert h('echo "a#b"') == '<span class="token function">echo</span> "a#b"'
    assert h("") == ""


def test_PlantUML_はテーマを読み込み_startuml_を省いてもよい() -> None:
    bare = build_docs.plantuml_source("a -> b\n")
    assert bare.startswith("@startuml\n!include ") and bare.endswith("@enduml\n")
    wbs = build_docs.plantuml_source("@startwbs\n* a\n@endwbs\n")
    assert wbs.splitlines()[0] == "@startwbs" and wbs.splitlines()[1].startswith("!include ")
