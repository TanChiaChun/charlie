"""Build per-user JSON data."""

import csv
import datetime as dt
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import cast


@dataclass
class UserDataInputs:
    """Data required to generate per-user JSON files."""

    user_public_ids: dict[str, str]
    daily_steps_by_user: dict[str, dict[str, int]]
    daily_stats: dict[dt.date, dict[str, dict[str, int | None]]]
    weekly_stats: dict[dt.date, dict[str, dict[str, int | float | None]]]
    streaks_5k_stats: dict[str, dict[str, int | dt.date | None]]


DATA_DIR = Path("..", "charlie-data", "data")
MIN_DATE = dt.date(2026, 10, 12)
PUBLIC_DIR = Path("public")
RAW_DATA_DIR = DATA_DIR / "raw"


def calculate_5k_streaks_stats(
    daily_steps_by_user: dict[str, dict[str, int]],
    last_fetch_date: dt.date,
    registered_users: set[str],
) -> dict[str, dict[str, int | dt.date | None]]:
    """Calculate 5K streak statistics and longest-streak rankings for users."""
    streaks_stats = {}

    for user in registered_users:
        daily_steps = {
            parse_date_string(date, 2026): steps
            for date, steps in daily_steps_by_user.get(user, {}).items()
        }
        streaks_stats[user] = calculate_user_5k_streaks(
            daily_steps, last_fetch_date
        )

    ranks = rank_users(
        {
            user: cast(int, stats["longest5kStreak"])
            for user, stats in streaks_stats.items()
        }
    )
    for user, stats in streaks_stats.items():
        stats["longest5kStreakRank"] = ranks.get(user)

    return streaks_stats


def calculate_daily_stats(
    daily_steps_by_user: dict[str, dict[str, int]],
    last_fetch_date: dt.date,
    registered_users: set[str],
    num_days: int = 2,
) -> dict[dt.date, dict[str, dict[str, int | None]]]:
    """Calculate daily steps and ranks for registered users."""
    daily_stats = {}

    for offset in range(num_days):
        target_date = last_fetch_date - dt.timedelta(days=offset)
        target_date_key = target_date.strftime("%m/%d")

        steps_by_user = {
            user: daily_steps_by_user.get(user, {}).get(target_date_key, 0)
            for user in registered_users
        }
        daily_ranks = rank_users(steps_by_user)
        daily_stats[target_date] = {
            user: {
                "todaySteps": steps_by_user.get(user, 0),
                "dailyRank": daily_ranks.get(user),
            }
            for user in registered_users
        }

    return daily_stats


def calculate_user_5k_streaks(
    daily_steps: dict[dt.date, int], today: dt.date
) -> dict[str, int | dt.date | None]:
    """Calculate a user's current and longest 5K streaks.

    A qualifying day has at least 5000 steps. Missing dates count as zero steps.
    Today's streak is provisional: if today's steps are below 5000, calculate
    streaks only through yesterday.
    """
    five_k_threshold = 5000
    current_cutoff = (
        today
        if daily_steps.get(today, 0) >= five_k_threshold
        else today - dt.timedelta(days=1)
    )

    longest_length = 0
    longest_start = None
    longest_end = None
    current_length = 0
    current_start = None
    current_end = None
    processing_length = 0
    processing_start = None

    day = MIN_DATE
    while day <= current_cutoff:
        if daily_steps.get(day, 0) >= five_k_threshold:
            if processing_length == 0:
                processing_start = day
            processing_length += 1
        else:
            if processing_length > longest_length:
                longest_length = processing_length
                longest_start = processing_start
                longest_end = day - dt.timedelta(days=1)
            processing_length = 0
            processing_start = None
        day += dt.timedelta(days=1)

    if processing_length:
        if processing_length > longest_length:
            longest_length = processing_length
            longest_start = processing_start
            longest_end = current_cutoff
        current_length = processing_length
        current_start = processing_start
        current_end = current_cutoff

    return {
        "longest5kStreak": longest_length,
        "longest5kStreakStart": longest_start,
        "longest5kStreakEnd": longest_end,
        "current5kStreak": current_length,
        "current5kStreakStart": current_start,
        "current5kStreakEnd": current_end,
    }


def calculate_weekly_stats(
    daily_steps_by_user: dict[str, dict[str, int]],
    end_date: dt.date,
    registered_users: set[str],
) -> dict[dt.date, dict[str, dict[str, int | float | None]]]:
    """Calculate weekly average steps and ranks for registered users."""
    weekly_stats = {}

    week_start = MIN_DATE
    while week_start <= end_date:
        week_end = min(
            week_start + dt.timedelta(days=6 - week_start.weekday()), end_date
        )

        num_days = (week_end - week_start).days + 1
        dates = [
            (week_start + dt.timedelta(days=offset)).strftime("%m/%d")
            for offset in range(num_days)
        ]

        weekly_averages = {}
        for user in registered_users:
            total_steps = sum(
                daily_steps_by_user.get(user, {}).get(date, 0) for date in dates
            )
            weekly_averages[user] = total_steps / len(dates)
        weekly_ranks = rank_users(weekly_averages)
        weekly_stats[week_start] = {
            user: {
                "weeklyAverage": weekly_averages[user],
                "weeklyRank": weekly_ranks.get(user),
            }
            for user in registered_users
        }

        week_start = week_end + dt.timedelta(days=1)

    return weekly_stats


def format_date(value: dt.date | None) -> str | None:
    """Format a date as an ISO string, preserving None."""
    return value.isoformat() if value else None


def get_last_fetch() -> str:
    """Get the timestamp of the latest raw data in ISO format."""
    latest_dir = max(RAW_DATA_DIR.iterdir())
    latest_file = max(latest_dir.iterdir())

    return dt.datetime.strptime(latest_file.stem, "%Y%m%d%H%M%S").isoformat()


def get_recent_daily_steps(
    daily_steps: dict[str, int], last_fetch_date: dt.date
) -> dict[str, int]:
    """Return daily steps for the most recent 10 days."""
    start_date = last_fetch_date - dt.timedelta(days=9)

    return {
        date: steps
        for date, steps in daily_steps.items()
        if start_date
        <= parse_date_string(date, last_fetch_date.year)
        <= last_fetch_date
    }


def load_daily_steps_by_user(
    registered_users: set[str],
) -> dict[str, dict[str, int]]:
    """Load daily steps for each registered user.

    Args:
        registered_users: Usernames to include.

    Returns:
        Mapping of usernames to daily steps, with dates as keys and step counts
        as values.
    """
    daily_steps_by_user: dict[str, dict[str, int]] = {}

    csv_paths = sorted(RAW_DATA_DIR.glob("*/*.csv"), reverse=True)
    for csv_path in csv_paths:
        with open(csv_path, encoding="utf-8", newline="") as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for username, steps, date in csv_reader:
                if (
                    username not in registered_users
                    or parse_date_string(date, 2026) < MIN_DATE
                ):
                    continue

                user_steps = daily_steps_by_user.setdefault(username, {})
                if date not in user_steps:
                    user_steps[date] = int(steps)

    return daily_steps_by_user


def load_user_public_ids() -> dict[str, str]:
    """Load user public IDs from the JSON file."""
    path = DATA_DIR / "output" / "user_public_ids.json"

    return cast(
        dict[str, str],
        json.loads(path.read_text(encoding="utf-8")),
    )


def parse_date_string(date_string: str, year: int) -> dt.date:
    """Parse an MM/DD date string into a date using the given year."""
    return dt.date.strptime(f"{year}/{date_string}", "%Y/%m/%d")


def rank_users(user_scores: Mapping[str, int | float]) -> dict[str, int]:
    """Rank by descending score, sharing ties and excluding zero scores."""
    sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)

    ranks = {}
    previous_score = None
    previous_rank = 0
    for position, (user, score) in enumerate(sorted_users, start=1):
        if score <= 0:
            break

        if score != previous_score:
            previous_rank = position

        ranks[user] = previous_rank
        previous_score = score

    return ranks


def write_leaderboard_json_file(
    daily_stats: dict[dt.date, dict[str, dict[str, int | None]]],
    weekly_stats: dict[dt.date, dict[str, dict[str, int | float | None]]],
    last_fetch: str,
) -> None:
    """Write leaderboard data to a JSON file."""
    daily_leaderboard = {}
    for date, user_stats in daily_stats.items():
        sorted_user_stats = sorted(
            (
                (user, stats)
                for user, stats in user_stats.items()
                if stats["dailyRank"] is not None and stats["dailyRank"] <= 10
            ),
            key=lambda x: (x[1]["dailyRank"], x[0].casefold()),
        )
        daily_leaderboard[date.isoformat()] = [
            {
                "rank": stats["dailyRank"],
                "steps": stats["todaySteps"],
                "username": user,
            }
            for user, stats in sorted_user_stats
        ]

    weekly_leaderboard = {}
    for week_start, week_stats in weekly_stats.items():
        sorted_week_stats = sorted(
            (
                (user, stats)
                for user, stats in week_stats.items()
                if stats["weeklyRank"] is not None and stats["weeklyRank"] <= 10
            ),
            key=lambda x: (x[1]["weeklyRank"], x[0].casefold()),
        )
        weekly_leaderboard[week_start.isoformat()] = [
            {
                "rank": stats["weeklyRank"],
                "averageSteps": stats["weeklyAverage"],
                "username": user,
            }
            for user, stats in sorted_week_stats
        ]

    leaderboard_data = {
        "lastFetch": last_fetch,
        "daily": daily_leaderboard,
        "weekly": weekly_leaderboard,
    }

    PUBLIC_DIR.mkdir(exist_ok=True)
    (PUBLIC_DIR / "leaderboard.json").write_text(
        json.dumps(leaderboard_data, ensure_ascii=False, indent=2)
    )


def write_user_json_files(
    inputs: UserDataInputs,
    last_fetch: str,
    last_fetch_date: dt.date,
) -> None:
    """Write per-user JSON files to the public users directory."""
    output_dir = PUBLIC_DIR / "users"
    output_dir.mkdir(parents=True, exist_ok=True)

    current_week_start = max(inputs.weekly_stats)
    for username, public_id in inputs.user_public_ids.items():
        daily_stats = inputs.daily_stats[last_fetch_date].get(username, {})
        weekly_stats = inputs.weekly_stats[current_week_start].get(username, {})
        streaks_5k_stats = inputs.streaks_5k_stats.get(username, {})

        user_data = {
            "username": username,
            "lastFetch": last_fetch,
            "dailySteps": get_recent_daily_steps(
                inputs.daily_steps_by_user.get(username, {}), last_fetch_date
            ),
            "stats": {
                "dailyRank": daily_stats.get("dailyRank"),
                "weeklyAverage": weekly_stats.get("weeklyAverage", 0),
                "weeklyRank": weekly_stats.get("weeklyRank"),
                "longest5kStreak": streaks_5k_stats.get("longest5kStreak", 0),
                "longest5kStreakRank": streaks_5k_stats.get(
                    "longest5kStreakRank"
                ),
                "longest5kStreakStart": format_date(
                    cast(
                        dt.date | None,
                        streaks_5k_stats.get("longest5kStreakStart"),
                    )
                ),
                "longest5kStreakEnd": format_date(
                    cast(
                        dt.date | None,
                        streaks_5k_stats.get("longest5kStreakEnd"),
                    )
                ),
                "current5kStreak": streaks_5k_stats.get("current5kStreak", 0),
                "current5kStreakStart": format_date(
                    cast(
                        dt.date | None,
                        streaks_5k_stats.get("current5kStreakStart"),
                    )
                ),
                "current5kStreakEnd": format_date(
                    cast(
                        dt.date | None,
                        streaks_5k_stats.get("current5kStreakEnd"),
                    )
                ),
            },
        }
        (output_dir / f"{public_id}.json").write_text(
            json.dumps(user_data, ensure_ascii=False, indent=2)
        )


def main() -> None:
    """Main function."""
    last_fetch = get_last_fetch()
    last_fetch_date = dt.datetime.fromisoformat(last_fetch).date()

    user_public_ids = load_user_public_ids()
    registered_users = set(user_public_ids)

    daily_steps_by_user = load_daily_steps_by_user(registered_users)

    daily_stats = calculate_daily_stats(
        daily_steps_by_user, last_fetch_date, registered_users
    )
    weekly_stats = calculate_weekly_stats(
        daily_steps_by_user,
        last_fetch_date,
        registered_users,
    )
    streaks_5k_stats = calculate_5k_streaks_stats(
        daily_steps_by_user, last_fetch_date, registered_users
    )

    write_user_json_files(
        UserDataInputs(
            user_public_ids,
            daily_steps_by_user,
            daily_stats,
            weekly_stats,
            streaks_5k_stats,
        ),
        last_fetch,
        last_fetch_date,
    )
    write_leaderboard_json_file(daily_stats, weekly_stats, last_fetch)


if __name__ == "__main__":
    main()
