from pathlib import Path

import pytest
from curriculum import (
    duration_minutes,
    knowledge_map_tags,
    parse_header,
    read_curriculum,
    readings,
    sessions,
    tag_ancestors,
    tag_matches,
)


@pytest.fixture(scope="module")
def text() -> str:
    return read_curriculum()


def test_全回が1から連番で読み取れる(text: str) -> None:
    result = sessions(text)
    assert [s.number for s in result] == list(range(1, len(result) + 1))
    assert result[1].tags == ("linux-シェル", "linux-アプリ", "linux-ネットワーク")
    assert result[0].duration.startswith("座学")


def test_知識体系マップのタグには大分野を含まない(text: str) -> None:
    tags = knowledge_map_tags(text)
    assert "http-リアルタイム" in tags
    assert "コンピュータ基盤" not in tags


def test_副読本の書名からリンクの記法を外す(text: str) -> None:
    titles = [r.title for r in readings(text)]
    assert "htmx 公式・Hypermedia Systems" in titles
    assert all("](" not in t for t in titles)


def test_上位タグはマップにあるものだけを返す() -> None:
    known = {"net", "net-http", "net-http-基本"}
    assert tag_ancestors("net-http-基本", known) == ["net", "net-http"]
    assert tag_ancestors("pm-見積", {"pm-見積"}) == []


@pytest.mark.parametrize(
    ("tag", "other", "expected"),
    [
        ("net-http-基本", "net-http", True),
        ("net-http", "net-http-基本", True),
        ("pm-見積", "pm", True),
        ("net-http", "net-社内", False),
        ("db", "db-sql", True),
        ("test-自動", "test-設計", False),
    ],
)
def test_タグの前方一致(tag: str, other: str, expected: bool) -> None:
    assert tag_matches(tag, other) is expected


def test_前提タグなしは空になる(tmp_path: Path) -> None:
    path = tmp_path / "README.md"
    path.write_text(
        "# 第1回 テーマ\ntag: a, b\n前提タグ: なし\n"
        "所要: 座学20分 / ハンズオン30分 / 振り返り10分\n",
        encoding="utf-8",
    )
    header = parse_header(path)
    assert header.tags == ("a", "b")
    assert header.prerequisites == ()


def test_所要を名前と分に分ける() -> None:
    assert duration_minutes("座学5分 / 発表35分 / 振り返り20分") == [
        ("座学", 5),
        ("発表", 35),
        ("振り返り", 20),
    ]
    with pytest.raises(ValueError, match="名前N分"):
        duration_minutes("座学20分、ハンズオン40分")


def test_冒頭の形式が違えばエラー(tmp_path: Path) -> None:
    path = tmp_path / "README.md"
    path.write_text("# 第1回 テーマ\ntags: a\n前提タグ: なし\n所要: x\n", encoding="utf-8")
    with pytest.raises(ValueError, match="2行目"):
        parse_header(path)
