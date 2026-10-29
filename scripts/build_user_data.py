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
    """Rank users by score in descending order, excluding zero scores."""
    sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)

    return {
        user: rank
        for rank, (user, score) in enumerate(sorted_users, start=1)
        if score > 0
    }


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

    user_public_ids = load_user_public_ids()
    registered_users = set(user_public_ids)

    daily_steps_by_user = load_daily_steps_by_user(registered_users)

    daily_ranks = calculate_daily_ranks(
        daily_steps_by_user, last_fetch, registered_users
    )
    weekly_stats = calculate_weekly_stats(
        daily_steps_by_user,
        dt.datetime.fromisoformat(last_fetch).date(),
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
