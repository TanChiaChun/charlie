from pathlib import Path

import aggregate_user_steps
import pytest
from pytest_mock import MockerFixture


def test_load_users(mocker: MockerFixture) -> None:
    mocker.patch(
        "aggregate_user_steps.open",
        mocker.mock_open(read_data="username\nuser1\nuser2"),
    )
    assert aggregate_user_steps.load_users() == {"user1", "user2"}


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

    assert aggregate_user_steps.load_user_daily_steps({"user1", "user2"}) == {
        "user1": {"10/11": 8000, "10/12": 8500},
        "user2": {"10/11": 6000, "10/12": 6300},
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

    assert aggregate_user_steps.load_user_latest_steps(
        tmp_path, {"user1", "user2"}
    ) == {
        "user1": {"10/12": 15000},
        "user2": {"10/12": 12500},
    }
