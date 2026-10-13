from pathlib import Path

import build_distribution as dist


def test_配布物には_git_と講師用を含めず_見本と資料の版を含める(tmp_path: Path) -> None:
    out = tmp_path / "handsoff"
    assert dist.main([str(out)]) == 0
    assert not list(out.rglob(".git"))
    assert not list(out.rglob(".venv"))
    assert not list(out.rglob("instructor.md"))
    assert not (out / "handoff.md").exists()
    assert not (out / "docs" / "_template").exists()
    examples = out / "examples"
    assert (examples / "todo-app" / "pyproject.toml").exists()
    assert (examples / "todo-app-snapshots" / "session-06").is_dir()
    assert (examples / "todo-app-snapshots" / "session-12").is_dir()
    assert (examples / "session01" / "README.md").exists()
    assert (out / "docs" / "_build" / "html").is_dir()
    assert (out / "docs" / "_build" / "handsoff.pdf").exists()


def test_出力先が空でなければ作らない(tmp_path: Path) -> None:
    (tmp_path / "x").write_text("x", encoding="utf-8")
    assert dist.main([str(tmp_path)]) == 1
