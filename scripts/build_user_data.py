"""Build per-user JSON data."""

import csv
import datetime as dt
import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

DATA_DIR = Path("..", "charlie-data", "data")
MIN_DATE = dt.date(2026, 10, 12)
RAW_DATA_DIR = DATA_DIR / "raw"


def calculate_5k_streaks_stats(
    daily_steps_by_user: dict[str, dict[str, int]],
    today: dt.date,
    registered_users: set[str],
) -> dict[str, dict[str, int | dt.date | None]]:
    """Calculate 5K streak statistics and longest-streak rankings for users."""
    streaks_stats = {}

    for user in registered_users:
        daily_steps = {
            parse_date_string(date, 2026): steps
            for date, steps in daily_steps_by_user.get(user, {}).items()
        }
        streaks_stats[user] = calculate_user_5k_streaks(daily_steps, today)

    ranks = rank_users(
        {
            user: cast(int, stats["longest5kStreak"])
            for user, stats in streaks_stats.items()
        }
    )
    for user, stats in streaks_stats.items():
        stats["longest5kStreakRank"] = ranks.get(user)

    return streaks_stats


def calculate_daily_ranks(
    daily_steps_by_user: dict[str, dict[str, int]],
    last_fetch: str,
    registered_users: set[str],
) -> dict[str, int]:
    """Calculate daily ranks for registered users with nonzero steps."""
    latest_date_key = last_fetch[5:10].replace("-", "/")
    steps_by_user = {
        user: daily_steps_by_user.get(user, {}).get(latest_date_key, 0)
        for user in registered_users
    }

    daily_ranks = rank_users(steps_by_user)

    return daily_ranks


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
) -> dict[str, dict[str, int | float | None]]:
    """Calculate week-to-date average steps and ranks for registered users."""
    start_date = end_date - dt.timedelta(days=end_date.weekday())
    dates = [
        (start_date + dt.timedelta(days=offset)).strftime("%m/%d")
        for offset in range(end_date.weekday() + 1)
    ]

    weekly_averages = {}
    for user in registered_users:
        total_steps = sum(
            daily_steps_by_user.get(user, {}).get(date, 0) for date in dates
        )
        weekly_averages[user] = total_steps / len(dates)

    weekly_ranks = rank_users(weekly_averages)

    return {
        user: {
            "weeklyAverage": weekly_averages[user],
            "weeklyRank": weekly_ranks.get(user),
        }
        for user in registered_users
    }


def format_date(value: dt.date | None) -> str | None:
    """Format a date as an ISO string, preserving None."""
    return value.isoformat() if value else None


def get_last_fetch() -> str:
    """Get the timestamp of the latest raw data in ISO format."""
    latest_dir = max(RAW_DATA_DIR.iterdir())
    latest_file = max(latest_dir.iterdir())

    return dt.datetime.strptime(latest_file.stem, "%Y%m%d%H%M%S").isoformat()


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

    raw_data_dirs = sorted(RAW_DATA_DIR.iterdir())
    for raw_data_dir in raw_data_dirs:
        user_latest_steps = load_user_latest_steps(
            raw_data_dir, registered_users
        )
        for username, steps_by_date in user_latest_steps.items():
            daily_steps_by_user.setdefault(username, {}).update(steps_by_date)

    return daily_steps_by_user


def load_user_latest_steps(
    raw_data_dir: Path, registered_users: set[str]
) -> dict[str, dict[str, int]]:
    """Load the latest available steps for each registered user.

    Args:
        raw_data_dir: Directory containing raw CSV files.
        registered_users: Usernames to include.

    Returns:
        Mapping of usernames to their latest steps, with dates as keys and step
        counts as values.
    """
    csv_paths = sorted(raw_data_dir.iterdir(), reverse=True)

    user_latest_steps = {}
    for csv_path in csv_paths:
        with open(csv_path, encoding="utf-8", newline="") as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for username, steps, date in csv_reader:
                if (
                    username not in registered_users
                    or username in user_latest_steps
                ):
                    continue

                parsed_date = parse_date_string(date, 2026)
                if parsed_date >= MIN_DATE:
                    user_latest_steps[username] = {date: int(steps)}

        if user_latest_steps.keys() >= registered_users:
            break

    return user_latest_steps


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


def write_user_json_files(
    user_public_ids: dict[str, str],
    daily_steps_by_user: dict[str, dict[str, int]],
    last_fetch: str,
    daily_ranks: dict[str, int],
    weekly_stats: dict[str, dict[str, int | float | None]],
) -> None:
    """Write per-user JSON files to the public users directory.

    Args:
        user_public_ids: Mapping of usernames to public IDs.
        daily_steps_by_user: Mapping of usernames to daily step counts.
        last_fetch: Timestamp of the latest raw data in ISO format.
        daily_ranks: Mapping of usernames to their daily ranks.
        weekly_stats: Mapping of usernames to their weekly averages and ranks.
    """
    output_dir = Path("public", "users")
    output_dir.mkdir(parents=True, exist_ok=True)

    for username, public_id in user_public_ids.items():
        user_data = {
            "username": username,
            "lastFetch": last_fetch,
            "dailySteps": daily_steps_by_user.get(username, {}),
            "stats": {
                "dailyRank": daily_ranks.get(username),
                "weeklyAverage": weekly_stats.get(username, {}).get(
                    "weeklyAverage", 0
                ),
                "weeklyRank": weekly_stats.get(username, {}).get("weeklyRank"),
            },
        }
        (output_dir / f"{public_id}.json").write_text(
            json.dumps(user_data, ensure_ascii=False, indent=2)
        )


def main() -> None:
    """Main function."""
    last_fetch = get_last_fetch()
    today = dt.datetime.fromisoformat(last_fetch).date()

    user_public_ids = load_user_public_ids()
    registered_users = set(user_public_ids)

    daily_steps_by_user = load_daily_steps_by_user(registered_users)

    daily_ranks = calculate_daily_ranks(
        daily_steps_by_user, last_fetch, registered_users
    )
    weekly_stats = calculate_weekly_stats(
        daily_steps_by_user,
        today,
        registered_users,
    )

    write_user_json_files(
        user_public_ids,
        daily_steps_by_user,
        last_fetch,
        daily_ranks,
        weekly_stats,
    )


if __name__ == "__main__":
    main()
