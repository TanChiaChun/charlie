import datetime as dt
import json
from pathlib import Path

import pytest

import build_user_data


def test_calculate_5k_streaks_stats() -> None:
    daily_steps_by_user = {
        "user1": {"10/13": 6000, "10/12": 5000},
        "user2": {"10/13": 8000, "10/12": 7000},
        "user3": {"10/13": 3500, "10/12": 3000},
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


def test_calculate_daily_stats() -> None:
    daily_steps_by_user = {
        "user1": {"10/28": 8000},
        "user2": {"10/28": 10000},
        "user3": {"10/28": 0},
        "user4": {"10/27": 12000},
        "user5": {"10/28": 13000},
    }

    assert build_user_data.calculate_daily_stats(
        daily_steps_by_user,
        dt.date(2026, 10, 28),
        {"user1", "user2", "user3", "user4"},
    ) == {
        dt.date(2026, 10, 28): {
            "user1": {"todaySteps": 8000, "dailyRank": 2},
            "user2": {"todaySteps": 10000, "dailyRank": 1},
            "user3": {"todaySteps": 0, "dailyRank": None},
            "user4": {"todaySteps": 0, "dailyRank": None},
        },
        dt.date(2026, 10, 27): {
            "user1": {"todaySteps": 0, "dailyRank": None},
            "user2": {"todaySteps": 0, "dailyRank": None},
            "user3": {"todaySteps": 0, "dailyRank": None},
            "user4": {"todaySteps": 12000, "dailyRank": 1},
        },
    }


def test_calculate_monthly_stats() -> None:
    daily_steps_by_user = {
        "user1": {"11/01": 13327, "10/31": 14668},
        "user2": {"11/02": 15033, "11/01": 11276, "10/31": 16056},
    }
    assert build_user_data.calculate_monthly_stats(
        daily_steps_by_user, dt.date(2026, 11, 2), {"user1", "user2"}
    ) == {
        "user1": {"monthlyAverage": 6663.5, "monthlyRank": 2},
        "user2": {"monthlyAverage": 13154.5, "monthlyRank": 1},
    }


def test_calculate_user_5k_streaks() -> None:
    start_date = build_user_data.MIN_DATE
    today = start_date + dt.timedelta(days=5)
    daily_steps = {
        today: 9000,
        start_date + dt.timedelta(days=4): 8000,
        start_date + dt.timedelta(days=3): 3000,
        start_date + dt.timedelta(days=2): 7000,
        start_date + dt.timedelta(days=1): 6000,
        start_date: 5000,
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
        "user1": {"10/27": 9680, "10/26": 10190, "10/25": 3500},
        "user2": {"10/27": 14964, "10/26": 5316, "10/25": 2100},
        "user3": {"10/25": 5600},
        "user4": {"10/26": 5702},
    }
    assert build_user_data.calculate_weekly_stats(
        daily_steps_by_user,
        dt.date(2026, 10, 27),
        {"user1", "user2", "user3"},
    ) == {
        dt.date(2026, 10, 12): {
            "user1": {"weeklyAverage": 0.0, "weeklyRank": None},
            "user2": {"weeklyAverage": 0.0, "weeklyRank": None},
            "user3": {"weeklyAverage": 0.0, "weeklyRank": None},
        },
        dt.date(2026, 10, 19): {
            "user1": {"weeklyAverage": 500.0, "weeklyRank": 2},
            "user2": {"weeklyAverage": 300.0, "weeklyRank": 3},
            "user3": {"weeklyAverage": 800.0, "weeklyRank": 1},
        },
        dt.date(2026, 10, 26): {
            "user1": {"weeklyAverage": 9935.0, "weeklyRank": 2},
            "user2": {"weeklyAverage": 10140.0, "weeklyRank": 1},
            "user3": {"weeklyAverage": 0.0, "weeklyRank": None},
        },
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


def test_get_recent_daily_steps() -> None:
    daily_steps = {
        "11/09": 1664,
        "11/08": 14925,
        "11/07": 12897,
        "11/06": 15683,
        "11/05": 13358,
        "11/04": 12773,
        "11/03": 12330,
        "11/02": 12060,
        "10/31": 14668,
        "10/30": 15049,
    }
    result = build_user_data.get_recent_daily_steps(
        daily_steps, dt.date(2026, 11, 9)
    )

    assert result == {
        "11/09": 1664,
        "11/08": 14925,
        "11/07": 12897,
        "11/06": 15683,
        "11/05": 13358,
        "11/04": 12773,
        "11/03": 12330,
        "11/02": 12060,
        "10/31": 14668,
    }


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
    (raw_data_root / "20261014").mkdir(parents=True)
    (raw_data_root / "20261014" / "20261014020501.csv").write_text(
        "username,steps,date\nuser1,9000,10/13\nuser2,13000,10/13\n"
    )

    assert build_user_data.load_daily_steps_by_user({"user1", "user2"}) == {
        "user1": {"10/13": 9000, "10/12": 8500},
        "user2": {"10/13": 13000, "10/12": 6300},
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


def test_write_leaderboard_json_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(build_user_data, "PUBLIC_DIR", tmp_path)

    daily_stats: dict[dt.date, dict[str, dict[str, int | None]]] = {
        dt.date(2026, 11, 6): {},
        dt.date(2026, 11, 5): {
            "user1": {"todaySteps": 10339, "dailyRank": 1},
            "user2": {"todaySteps": 6215, "dailyRank": 3},
            "User3": {"todaySteps": 10339, "dailyRank": 1},
            "user9": {"todaySteps": 5159, "dailyRank": 5},
            "user5": {"todaySteps": 2663, "dailyRank": 9},
            "user11": {"todaySteps": 2351, "dailyRank": 11},
            "user8": {"todaySteps": 3318, "dailyRank": 8},
            "user12": {"todaySteps": 0, "dailyRank": None},
            "user10": {"todaySteps": 5060, "dailyRank": 6},
            "user7": {"todaySteps": 3592, "dailyRank": 7},
            "user6": {"todaySteps": 2515, "dailyRank": 10},
            "user4": {"todaySteps": 5818, "dailyRank": 4},
        },
    }
    weekly_stats: dict[dt.date, dict[str, dict[str, int | float | None]]] = {
        dt.date(2026, 10, 26): {
            "user1": {"weeklyAverage": 16367.0, "weeklyRank": 2},
            "user2": {"weeklyAverage": 15190.0, "weeklyRank": 5},
            "user3": {"weeklyAverage": 13276.0, "weeklyRank": 10},
            "user4": {"weeklyAverage": 16097.0, "weeklyRank": 3},
            "user5": {"weeklyAverage": 14618.0, "weeklyRank": 6},
            "user6": {"weeklyAverage": 13432.0, "weeklyRank": 9},
            "user7": {"weeklyAverage": 18759.0, "weeklyRank": 1},
            "user8": {"weeklyAverage": 14389.0, "weeklyRank": 7},
            "user9": {"weeklyAverage": 13468.0, "weeklyRank": 8},
            "user10": {"weeklyAverage": 13000.0, "weeklyRank": 11},
            "user11": {"weeklyAverage": 15739.0, "weeklyRank": 4},
            "user12": {"weeklyAverage": 0.0, "weeklyRank": None},
        },
        dt.date(2026, 11, 2): {
            "user8": {"weeklyRank": 4, "weeklyAverage": 17086.0},
            "user1": {"weeklyRank": 9, "weeklyAverage": 13464.0},
            "user2": {"weeklyRank": 3, "weeklyAverage": 17890.0},
            "user10": {"weeklyRank": 2, "weeklyAverage": 23330.0},
            "user5": {"weeklyRank": 6, "weeklyAverage": 16294.0},
            "user3": {"weeklyRank": 8, "weeklyAverage": 14840.0},
            "user7": {"weeklyRank": 1, "weeklyAverage": 34088.0},
            "user4": {"weeklyRank": 5, "weeklyAverage": 16795.0},
            "user6": {"weeklyRank": 7, "weeklyAverage": 15436.0},
        },
    }
    monthly_stats: dict[str, dict[str, int | float | None]] = {
        "User1": {"monthlyAverage": 19266.8, "monthlyRank": 1},
        "User2": {"monthlyAverage": 16451.5, "monthlyRank": 2},
        "User3": {"monthlyAverage": 15750.2, "monthlyRank": 3},
        "User4": {"monthlyAverage": 14156.7, "monthlyRank": 4},
        "User5": {"monthlyAverage": 13564.8, "monthlyRank": 5},
        "User6": {"monthlyAverage": 13433.7, "monthlyRank": 6},
        "User7": {"monthlyAverage": 13388.6, "monthlyRank": 7},
        "User8": {"monthlyAverage": 13343.6, "monthlyRank": 8},
        "User9": {"monthlyAverage": 13266.0, "monthlyRank": 9},
        "User10": {"monthlyAverage": 13060.4, "monthlyRank": 10},
        "User11": {"monthlyAverage": 12865.4, "monthlyRank": 11},
        "User12": {"monthlyAverage": 11979.9, "monthlyRank": 12},
        "User13": {"monthlyAverage": 11744.8, "monthlyRank": 13},
        "User14": {"monthlyAverage": 11732.7, "monthlyRank": 14},
        "User15": {"monthlyAverage": 11627.8, "monthlyRank": 15},
        "User16": {"monthlyAverage": 11259.7, "monthlyRank": 16},
        "User17": {"monthlyAverage": 10943.2, "monthlyRank": 17},
        "User18": {"monthlyAverage": 10572.9, "monthlyRank": 18},
        "User19": {"monthlyAverage": 10143.2, "monthlyRank": 19},
        "User20": {"monthlyAverage": 10113.5, "monthlyRank": 20},
    }
    streaks_5k_stats: dict[str, dict[str, int | dt.date | None]] = {
        "User1": {"longest5kStreak": 17, "longest5kStreakRank": 9},
        "User2": {"longest5kStreak": 23, "longest5kStreakRank": 5},
        "User3": {"longest5kStreak": 29, "longest5kStreakRank": 1},
        "User4": {"longest5kStreak": 22, "longest5kStreakRank": 6},
        "User5": {"longest5kStreak": 20, "longest5kStreakRank": 7},
        "User6": {"longest5kStreak": 29, "longest5kStreakRank": 1},
        "User7": {"longest5kStreak": 24, "longest5kStreakRank": 4},
        "User8": {"longest5kStreak": 18, "longest5kStreakRank": 8},
        "User9": {"longest5kStreak": 17, "longest5kStreakRank": 9},
        "User10": {"longest5kStreak": 29, "longest5kStreakRank": 1},
        "User11": {"longest5kStreak": 17, "longest5kStreakRank": 9},
    }
    build_user_data.write_leaderboard_json_file(
        daily_stats,
        weekly_stats,
        monthly_stats,
        streaks_5k_stats,
        "2026-11-06T07:05:02",
    )

    result = json.loads((tmp_path / "leaderboard.json").read_text())

    assert result["lastFetch"] == "2026-11-06T07:05:02"

    assert len(result["daily"]) == 2
    assert len(result["daily"]["2026-11-06"]) == 0
    assert len(result["daily"]["2026-11-05"]) == 10
    assert result["daily"]["2026-11-05"] == [
        {"rank": 1, "steps": 10339, "username": "user1"},
        {"rank": 1, "steps": 10339, "username": "User3"},
        {"rank": 3, "steps": 6215, "username": "user2"},
        {"rank": 4, "steps": 5818, "username": "user4"},
        {"rank": 5, "steps": 5159, "username": "user9"},
        {"rank": 6, "steps": 5060, "username": "user10"},
        {"rank": 7, "steps": 3592, "username": "user7"},
        {"rank": 8, "steps": 3318, "username": "user8"},
        {"rank": 9, "steps": 2663, "username": "user5"},
        {"rank": 10, "steps": 2515, "username": "user6"},
    ]

    assert len(result["weekly"]) == 2
    assert len(result["weekly"]["2026-10-26"]) == 10
    assert len(result["weekly"]["2026-11-02"]) == 9
    assert result["weekly"]["2026-10-26"] == [
        {"rank": 1, "averageSteps": 18759.0, "username": "user7"},
        {"rank": 2, "averageSteps": 16367.0, "username": "user1"},
        {"rank": 3, "averageSteps": 16097.0, "username": "user4"},
        {"rank": 4, "averageSteps": 15739.0, "username": "user11"},
        {"rank": 5, "averageSteps": 15190.0, "username": "user2"},
        {"rank": 6, "averageSteps": 14618.0, "username": "user5"},
        {"rank": 7, "averageSteps": 14389.0, "username": "user8"},
        {"rank": 8, "averageSteps": 13468.0, "username": "user9"},
        {"rank": 9, "averageSteps": 13432.0, "username": "user6"},
        {"rank": 10, "averageSteps": 13276.0, "username": "user3"},
    ]

    assert len(result["monthly"]) == 20
    assert result["monthly"] == [
        {"rank": 1, "averageSteps": 19266.8, "username": "User1"},
        {"rank": 2, "averageSteps": 16451.5, "username": "User2"},
        {"rank": 3, "averageSteps": 15750.2, "username": "User3"},
        {"rank": 4, "averageSteps": 14156.7, "username": "User4"},
        {"rank": 5, "averageSteps": 13564.8, "username": "User5"},
        {"rank": 6, "averageSteps": 13433.7, "username": "User6"},
        {"rank": 7, "averageSteps": 13388.6, "username": "User7"},
        {"rank": 8, "averageSteps": 13343.6, "username": "User8"},
        {"rank": 9, "averageSteps": 13266.0, "username": "User9"},
        {"rank": 10, "averageSteps": 13060.4, "username": "User10"},
        {"rank": 11, "averageSteps": 12865.4, "username": "User11"},
        {"rank": 12, "averageSteps": 11979.9, "username": "User12"},
        {"rank": 13, "averageSteps": 11744.8, "username": "User13"},
        {"rank": 14, "averageSteps": 11732.7, "username": "User14"},
        {"rank": 15, "averageSteps": 11627.8, "username": "User15"},
        {"rank": 16, "averageSteps": 11259.7, "username": "User16"},
        {"rank": 17, "averageSteps": 10943.2, "username": "User17"},
        {"rank": 18, "averageSteps": 10572.9, "username": "User18"},
        {"rank": 19, "averageSteps": 10143.2, "username": "User19"},
        {"rank": 20, "averageSteps": 10113.5, "username": "User20"},
    ]

    assert len(result["streaks5k"]) == 11
    assert result["streaks5k"] == [
        {"rank": 1, "days": 29, "username": "User10"},
        {"rank": 1, "days": 29, "username": "User3"},
        {"rank": 1, "days": 29, "username": "User6"},
        {"rank": 4, "days": 24, "username": "User7"},
        {"rank": 5, "days": 23, "username": "User2"},
        {"rank": 6, "days": 22, "username": "User4"},
        {"rank": 7, "days": 20, "username": "User5"},
        {"rank": 8, "days": 18, "username": "User8"},
        {"rank": 9, "days": 17, "username": "User1"},
        {"rank": 9, "days": 17, "username": "User11"},
        {"rank": 9, "days": 17, "username": "User9"},
    ]


def test_write_user_json_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)

    user_public_ids = {"user1": "token1", "user2": "token2"}
    daily_steps_by_user = {
        "user1": {
            "11/08": 14925,
            "11/07": 12897,
            "11/06": 15683,
            "11/05": 13358,
            "11/04": 12773,
            "11/03": 12330,
            "10/29": 11649,
        }
    }
    daily_stats: dict[dt.date, dict[str, dict[str, int | None]]] = {
        dt.date(2026, 11, 8): {"user1": {"todaySteps": 14925, "dailyRank": 1}}
    }
    weekly_stats: dict[dt.date, dict[str, dict[str, int | float | None]]] = {
        dt.date(2026, 11, 2): {
            "user1": {"weeklyAverage": 13432.3, "weeklyRank": 9}
        },
        dt.date(2026, 11, 9): {
            "user1": {"weeklyAverage": 9469.0, "weeklyRank": 10}
        },
    }
    monthly_stats: dict[str, dict[str, int | float | None]] = {
        "user1": {"monthlyAverage": 13085.2, "monthlyRank": 1},
    }
    streaks_5k_stats: dict[str, dict[str, int | dt.date | None]] = {
        "user1": {
            "longest5kStreak": 3,
            "longest5kStreakRank": 1,
            "longest5kStreakStart": dt.date(2026, 11, 3),
            "longest5kStreakEnd": dt.date(2026, 11, 5),
            "current5kStreak": 2,
            "current5kStreakStart": dt.date(2026, 11, 7),
            "current5kStreakEnd": dt.date(2026, 11, 8),
        }
    }
    user_data_inputs = build_user_data.UserDataInputs(
        user_public_ids,
        daily_steps_by_user,
        daily_stats,
        weekly_stats,
        monthly_stats,
        streaks_5k_stats,
    )
    build_user_data.write_user_json_files(
        user_data_inputs,
        "2026-11-08T23:05:02",
        dt.date(2026, 11, 8),
    )

    output_dir = Path("public", "users")
    assert json.loads((output_dir / "token1.json").read_text()) == {
        "username": "user1",
        "lastFetch": "2026-11-08T23:05:02",
        "dailySteps": {
            "11/08": 14925,
            "11/07": 12897,
            "11/06": 15683,
            "11/05": 13358,
            "11/04": 12773,
            "11/03": 12330,
        },
        "stats": {
            "dailyRank": 1,
            "weeklyAverage": 9469.0,
            "weeklyRank": 10,
            "monthlyAverage": 13085.2,
            "monthlyRank": 1,
            "longest5kStreak": 3,
            "longest5kStreakRank": 1,
            "longest5kStreakStart": "2026-11-03",
            "longest5kStreakEnd": "2026-11-05",
            "current5kStreak": 2,
            "current5kStreakStart": "2026-11-07",
            "current5kStreakEnd": "2026-11-08",
        },
    }
    assert json.loads((output_dir / "token2.json").read_text()) == {
        "username": "user2",
        "lastFetch": "2026-11-08T23:05:02",
        "dailySteps": {},
        "stats": {
            "dailyRank": None,
            "weeklyAverage": 0.0,
            "weeklyRank": None,
            "monthlyAverage": 0.0,
            "monthlyRank": None,
            "longest5kStreak": 0,
            "longest5kStreakRank": None,
            "longest5kStreakStart": None,
            "longest5kStreakEnd": None,
            "current5kStreak": 0,
            "current5kStreakStart": None,
            "current5kStreakEnd": None,
        },
    }
