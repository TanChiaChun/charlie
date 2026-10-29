import datetime as dt
import json
from pathlib import Path

import pytest

import build_user_data


def test_calculate_5k_streaks_stats() -> None:
    daily_steps_by_user = {
        "user1": {"10/12": 5000, "10/13": 6000},
        "user2": {"10/12": 7000, "10/13": 8000},
        "user3": {"10/12": 3000, "10/13": 3500},
    }

    stats = build_user_data.calculate_5k_streaks_stats(
        daily_steps_by_user,
        build_user_data.MIN_DATE + dt.timedelta(days=2),
        {"user1", "user2", "user3"},
    )
    assert stats["user1"]["longest5kStreak"] == 2
    assert stats["user1"]["longest5kStreakRank"] == 1
    assert stats["user2"]["longest5kStreak"] == 2
    assert stats["user2"]["longest5kStreakRank"] == 1
    assert stats["user3"]["longest5kStreak"] == 0
    assert stats["user3"]["longest5kStreakRank"] is None


def test_calculate_daily_ranks() -> None:
    daily_steps_by_user = {
        "user1": {"10/28": 8000},
        "user2": {"10/28": 10000},
        "user3": {"10/28": 0},
        "user4": {"10/27": 12000},
        "user5": {"10/28": 13000},
    }

    assert build_user_data.calculate_daily_ranks(
        daily_steps_by_user,
        "2026-10-28T23:05:02",
        {"user1", "user2", "user3", "user4"},
    ) == {"user1": 2, "user2": 1}


def test_calculate_user_5k_streaks() -> None:
    start_date = build_user_data.MIN_DATE
    today = start_date + dt.timedelta(days=5)
    daily_steps = {
        start_date: 5000,
        start_date + dt.timedelta(days=1): 6000,
        start_date + dt.timedelta(days=2): 7000,
        start_date + dt.timedelta(days=3): 3000,
        start_date + dt.timedelta(days=4): 8000,
        today: 9000,
    }

    assert build_user_data.calculate_user_5k_streaks(daily_steps, today) == {
        "longest5kStreak": 3,
        "longest5kStreakStart": start_date,
        "longest5kStreakEnd": start_date + dt.timedelta(days=2),
        "current5kStreak": 2,
        "current5kStreakStart": start_date + dt.timedelta(days=4),
        "current5kStreakEnd": today,
    }


def test_calculate_weekly_stats() -> None:
    daily_steps_by_user = {
        "user1": {
            "10/25": 10397,
            "10/26": 10190,
            "10/27": 9680,
        },
        "user2": {
            "10/25": 3432,
            "10/26": 5316,
            "10/27": 14964,
        },
        "user3": {
            "10/25": 12285,
        },
        "user4": {
            "10/26": 5702,
        },
    }
    assert build_user_data.calculate_weekly_stats(
        daily_steps_by_user,
        dt.date(2026, 10, 27),
        {"user1", "user2", "user3"},
    ) == {
        "user2": {"weeklyAverage": 10140.0, "weeklyRank": 1},
        "user1": {"weeklyAverage": 9935.0, "weeklyRank": 2},
        "user3": {"weeklyAverage": 0.0, "weeklyRank": None},
    }


def test_format_date() -> None:
    assert build_user_data.format_date(dt.date(2026, 10, 29)) == "2026-10-29"
    assert build_user_data.format_date(None) is None


def test_get_last_fetch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(build_user_data, "RAW_DATA_DIR", tmp_path)
    (tmp_path / "20261025").mkdir()
    (tmp_path / "20261026").mkdir()
    (tmp_path / "20261026" / "20261026000502.csv").touch()
    (tmp_path / "20261026" / "20261026010502.csv").touch()

    assert build_user_data.get_last_fetch() == "2026-10-26T01:05:02"


def test_load_daily_steps_by_user(
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

    assert build_user_data.load_daily_steps_by_user({"user1", "user2"}) == {
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


def test_parse_date_string() -> None:
    assert build_user_data.parse_date_string("10/29", 2026) == dt.date(
        2026, 10, 29
    )


def test_rank_users() -> None:
    assert build_user_data.rank_users(
        {
            "user1": 10000,
            "user2": 12000,
            "user3": 8000,
            "user4": 0,
            "user5": 10000,
        }
    ) == {"user2": 1, "user1": 2, "user5": 2, "user3": 4}


def test_write_user_json_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)

    build_user_data.write_user_json_files(
        build_user_data.UserDataInputs(
            {"user1": "token1", "user2": "token2"},
            {"user1": {"10/10": 10000}},
            {"user1": 1},
            {"user1": {"weeklyAverage": 9935.0, "weeklyRank": 1}},
            {
                "user1": {
                    "longest5kStreak": 3,
                    "longest5kStreakRank": 1,
                    "longest5kStreakStart": dt.date(2026, 10, 23),
                    "longest5kStreakEnd": dt.date(2026, 10, 25),
                    "current5kStreak": 2,
                    "current5kStreakStart": dt.date(2026, 10, 28),
                    "current5kStreakEnd": dt.date(2026, 10, 29),
                }
            },
        ),
        "2026-10-26T17:05:02",
    )

    output_dir = Path("public", "users")
    assert json.loads((output_dir / "token1.json").read_text()) == {
        "username": "user1",
        "lastFetch": "2026-10-26T17:05:02",
        "dailySteps": {"10/10": 10000},
        "stats": {
            "dailyRank": 1,
            "weeklyAverage": 9935.0,
            "weeklyRank": 1,
            "longest5kStreak": 3,
            "longest5kStreakRank": 1,
            "longest5kStreakStart": "2026-10-23",
            "longest5kStreakEnd": "2026-10-25",
            "current5kStreak": 2,
            "current5kStreakStart": "2026-10-28",
            "current5kStreakEnd": "2026-10-29",
        },
    }
    assert json.loads((output_dir / "token2.json").read_text()) == {
        "username": "user2",
        "lastFetch": "2026-10-26T17:05:02",
        "dailySteps": {},
        "stats": {
            "dailyRank": None,
            "weeklyAverage": 0.0,
            "weeklyRank": None,
            "longest5kStreak": 0,
            "longest5kStreakRank": None,
            "longest5kStreakStart": None,
            "longest5kStreakEnd": None,
            "current5kStreak": 0,
            "current5kStreakStart": None,
            "current5kStreakEnd": None,
        },
    }
