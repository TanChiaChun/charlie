import json
from pathlib import Path

import pytest

import build_user_data


def test_load_user_daily_steps(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    charlie_dir = tmp_path / "charlie"
    charlie_dir.mkdir()
    monkeypatch.chdir(charlie_dir)

    raw_data_root = tmp_path / "charlie-data" / "data" / "raw"
    (raw_data_root / "20261011").mkdir(parents=True)
    (raw_data_root / "20261011" / "20261011235501.csv").write_text(
        "username,steps,date\nuser1,8000,10/11\nuser2,6000,10/11\n"
    )
    (raw_data_root / "20261012").mkdir()
    (raw_data_root / "20261012" / "20261012235501.csv").write_text(
        "username,steps,date\nuser1,8500,10/12\nuser2,6300,10/12\n"
    )
    (raw_data_root / "20261013").mkdir(parents=True)
    (raw_data_root / "20261013" / "20261013235501.csv").write_text(
        "username,steps,date\nuser1,9000,10/13\nuser2,6500,10/13\n"
    )

    assert build_user_data.load_user_daily_steps({"user1", "user2"}) == {
        "user1": {"10/12": 8500, "10/13": 9000},
        "user2": {"10/12": 6300, "10/13": 6500},
    }


def test_load_user_latest_steps(tmp_path: Path) -> None:
    (tmp_path / "20261012235501.csv").write_text(
        "username,steps,date\nuser1,15000,10/12\nuser3,10000,10/12\n"
    )
    (tmp_path / "20261012233501.csv").write_text(
        "username,steps,date\n"
        "user1,13500,10/12\n"
        "user2,12500,10/12\n"
        "user3,15000,10/12\n"
    )

    assert build_user_data.load_user_latest_steps(
        tmp_path, {"user1", "user2"}
    ) == {
        "user1": {"10/12": 15000},
        "user2": {"10/12": 12500},
    }


def test_load_user_public_ids(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    project_dir = tmp_path / "charlie"
    project_dir.mkdir()
    monkeypatch.chdir(project_dir)

    output_dir = project_dir / ".." / "charlie-data" / "data" / "output"
    output_dir.mkdir(parents=True)
    (output_dir / "user_public_ids.json").write_text(
        '{\n  "user1": "token1",\n  "user2": "token2"\n}'
    )

    assert build_user_data.load_user_public_ids() == {
        "user1": "token1",
        "user2": "token2",
    }


def test_write_user_json_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)

    build_user_data.write_user_json_files(
        {"user1": "token1", "user2": "token2"},
        {"user1": {"10/10": 10000}},
    )

    output_dir = Path("public", "users")
    assert json.loads((output_dir / "token1.json").read_text()) == {
        "username": "user1",
        "dailySteps": {"10/10": 10000},
    }
    assert json.loads((output_dir / "token2.json").read_text()) == {
        "username": "user2",
        "dailySteps": {},
    }
