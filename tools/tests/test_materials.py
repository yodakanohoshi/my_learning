import random

import check_materials
import generate_session01_logs as logs


def test_資料の形式検査が通る() -> None:
    assert check_materials.main([]) == 0


def test_第1回のログは同じシードなら同じになる() -> None:
    random.seed(logs.SEED)
    first = logs.day_lines(logs.SPIKE_DAY)
    random.seed(logs.SEED)
    assert logs.day_lines(logs.SPIKE_DAY) == first


def test_第1回のログには仕込みが入っている() -> None:
    random.seed(logs.SEED)
    lines = logs.day_lines(logs.SPIKE_DAY)
    noon_locked = [
        line for line in lines if " 12:" in line and "ERROR [db] database is locked" in line
    ]
    assert len(noon_locked) >= 25
    assert any("backup started" in line for line in lines)
