"""Build per-user JSON data."""

import csv
import datetime as dt
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import NotRequired, TypedDict, cast

DATA_DIR = Path("..", "charlie-data", "data")
MIN_DATE = dt.date(2026, 10, 12)
PUBLIC_DIR = Path("public")
RAW_DATA_DIR = DATA_DIR / "raw"


class DailyStats(TypedDict):
    """Daily statistics for a user."""

    steps: int
    rank: int | None


class PeriodStats(TypedDict):
    """User statistics for a period."""

    averageSteps: float
    rank: int | None


class StreaksStats(TypedDict):
    """Streak statistics for a user."""

    longestStreak: int
    longestStreakStart: dt.date | None
    longestStreakEnd: dt.date | None
    currentStreak: int
    currentStreakStart: dt.date | None
    currentStreakEnd: dt.date | None
    longestStreakRank: NotRequired[int | None]


@dataclass
class UserDataInputs:
    """Data required to generate per-user JSON files."""

    user_public_ids: dict[str, str]
    user_teams: dict[str, str]
    daily_steps_by_user: dict[str, dict[str, int]]
    daily_stats: dict[dt.date, dict[str, DailyStats]]
    weekly_stats: dict[dt.date, dict[str, PeriodStats]]
    monthly_stats: dict[str, PeriodStats]
    streaks_5k_stats: dict[str, StreaksStats]


def calculate_5k_streaks_stats(
    daily_steps_by_user: dict[str, dict[str, int]],
    last_fetch_date: dt.date,
    registered_users: set[str],
) -> dict[str, StreaksStats]:
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

    ranks = rank_by_scores(
        {user: stats["longestStreak"] for user, stats in streaks_stats.items()}
    )
    for user, stats in streaks_stats.items():
        stats["longestStreakRank"] = ranks.get(user)

    return streaks_stats


def calculate_daily_stats(
    daily_steps_by_user: dict[str, dict[str, int]],
    last_fetch_date: dt.date,
    registered_users: set[str],
    num_days: int = 2,
) -> dict[dt.date, dict[str, DailyStats]]:
    """Calculate daily steps and ranks for registered users."""
    daily_stats: dict[dt.date, dict[str, DailyStats]] = {}

    for offset in range(num_days):
        target_date = last_fetch_date - dt.timedelta(days=offset)
        target_date_key = target_date.strftime("%m/%d")

        steps_by_user = {
            user: daily_steps_by_user.get(user, {}).get(target_date_key, 0)
            for user in registered_users
        }
        daily_ranks = rank_by_scores(steps_by_user)
        daily_stats[target_date] = {
            user: {
                "steps": steps_by_user.get(user, 0),
                "rank": daily_ranks.get(user),
            }
            for user in registered_users
        }

    return daily_stats


def calculate_monthly_stats(
    daily_steps_by_user: dict[str, dict[str, int]],
    end_date: dt.date,
    registered_users: set[str],
) -> dict[str, PeriodStats]:
    """Calculate monthly average steps and ranks for registered users."""
    month_start = end_date.replace(day=1)
    num_days = (end_date - month_start).days + 1
    dates = [
        (month_start + dt.timedelta(days=offset)).strftime("%m/%d")
        for offset in range(num_days)
    ]

    monthly_averages = {}
    for user in registered_users:
        total_steps = sum(
            daily_steps_by_user.get(user, {}).get(date, 0) for date in dates
        )
        monthly_averages[user] = total_steps / num_days
    monthly_ranks = rank_by_scores(monthly_averages)

    return {
        user: {
            "averageSteps": monthly_averages[user],
            "rank": monthly_ranks.get(user),
        }
        for user in registered_users
    }


def calculate_user_5k_streaks(
    daily_steps: dict[dt.date, int], today: dt.date
) -> StreaksStats:
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
        "longestStreak": longest_length,
        "longestStreakStart": longest_start,
        "longestStreakEnd": longest_end,
        "currentStreak": current_length,
        "currentStreakStart": current_start,
        "currentStreakEnd": current_end,
    }


def calculate_weekly_stats(
    daily_steps_by_user: dict[str, dict[str, int]],
    end_date: dt.date,
    registered_users: set[str],
) -> dict[dt.date, dict[str, PeriodStats]]:
    """Calculate weekly average steps and ranks for registered users."""
    weekly_stats: dict[dt.date, dict[str, PeriodStats]] = {}

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
            weekly_averages[user] = total_steps / num_days
        weekly_ranks = rank_by_scores(weekly_averages)
        weekly_stats[week_start] = {
            user: {
                "averageSteps": weekly_averages[user],
                "rank": weekly_ranks.get(user),
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


def load_user_teams() -> dict[str, str]:
    """Load user teams from the CSV file."""
    with open(
        Path(DATA_DIR, "input", "users.csv"), encoding="utf-8", newline=""
    ) as csv_file:
        csv_reader = csv.DictReader(csv_file)

        return {row["username"]: row["team"] for row in csv_reader}


def parse_date_string(date_string: str, year: int) -> dt.date:
    """Parse an MM/DD date string into a date using the given year."""
    return dt.date.strptime(f"{year}/{date_string}", "%Y/%m/%d")


def rank_by_scores(scores: Mapping[str, int | float]) -> dict[str, int]:
    """Rank by descending score, sharing ties and excluding zero scores."""
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    ranks = {}
    previous_score = None
    previous_rank = 0
    for position, (name, score) in enumerate(sorted_scores, start=1):
        if score <= 0:
            break

        if score != previous_score:
            previous_rank = position

        ranks[name] = previous_rank
        previous_score = score

    return ranks


def write_leaderboard_json_file(
    daily_stats: dict[dt.date, dict[str, DailyStats]],
    weekly_stats: dict[dt.date, dict[str, PeriodStats]],
    monthly_stats: dict[str, PeriodStats],
    streaks_5k_stats: dict[str, StreaksStats],
    last_fetch: str,
) -> None:
    """Write leaderboard data to a JSON file."""
    # pylint: disable=too-many-locals
    daily_leaderboard = {}
    for date, user_stats in daily_stats.items():
        sorted_user_stats = sorted(
            (
                (user, stats)
                for user, stats in user_stats.items()
                if stats["rank"] is not None and stats["rank"] <= 10
            ),
            key=lambda x: (x[1]["rank"], x[0].casefold()),
        )
        daily_leaderboard[date.isoformat()] = [
            {
                "rank": stats["rank"],
                "steps": stats["steps"],
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
                if stats["rank"] is not None and stats["rank"] <= 10
            ),
            key=lambda x: (x[1]["rank"], x[0].casefold()),
        )
        weekly_leaderboard[week_start.isoformat()] = [
            {
                "rank": stats["rank"],
                "averageSteps": stats["averageSteps"],
                "username": user,
            }
            for user, stats in sorted_week_stats
        ]

    sorted_monthly_stats = sorted(
        (
            (user, stats)
            for user, stats in monthly_stats.items()
            if stats["rank"] is not None and stats["rank"] <= 20
        ),
        key=lambda x: (x[1]["rank"], x[0].casefold()),
    )
    monthly_leaderboard = [
        {
            "rank": stats["rank"],
            "averageSteps": stats["averageSteps"],
            "username": user,
        }
        for user, stats in sorted_monthly_stats
    ]

    sorted_streaks_5k_stats = sorted(
        (
            (user, stats)
            for user, stats in streaks_5k_stats.items()
            if isinstance(stats["longestStreakRank"], int)
            and stats["longestStreakRank"] <= 10
        ),
        key=lambda x: (x[1]["longestStreakRank"], x[0].casefold()),
    )
    streaks_5k_leaderboard = [
        {
            "rank": stats["longestStreakRank"],
            "days": stats["longestStreak"],
            "username": user,
        }
        for user, stats in sorted_streaks_5k_stats
    ]

    leaderboard_data = {
        "lastFetch": last_fetch,
        "daily": daily_leaderboard,
        "weekly": weekly_leaderboard,
        "monthly": monthly_leaderboard,
        "streaks5k": streaks_5k_leaderboard,
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
        daily_stats: DailyStats = inputs.daily_stats[last_fetch_date].get(
            username, {"steps": 0, "rank": None}
        )
        weekly_stats: PeriodStats = inputs.weekly_stats[current_week_start].get(
            username, {"averageSteps": 0.0, "rank": None}
        )
        monthly_stats: PeriodStats = inputs.monthly_stats.get(
            username, {"averageSteps": 0.0, "rank": None}
        )
        streaks_5k_stats: StreaksStats = inputs.streaks_5k_stats.get(
            username,
            {
                "longestStreak": 0,
                "longestStreakStart": None,
                "longestStreakEnd": None,
                "currentStreak": 0,
                "currentStreakStart": None,
                "currentStreakEnd": None,
                "longestStreakRank": None,
            },
        )

        user_data = {
            "username": username,
            "team": inputs.user_teams[username],
            "lastFetch": last_fetch,
            "dailySteps": get_recent_daily_steps(
                inputs.daily_steps_by_user.get(username, {}), last_fetch_date
            ),
            "stats": {
                "dailyRank": daily_stats["rank"],
                "weeklyAverage": weekly_stats["averageSteps"],
                "weeklyRank": weekly_stats["rank"],
                "monthlyAverage": monthly_stats["averageSteps"],
                "monthlyRank": monthly_stats["rank"],
                "longest5kStreak": streaks_5k_stats["longestStreak"],
                "longest5kStreakRank": streaks_5k_stats["longestStreakRank"],
                "longest5kStreakStart": format_date(
                    streaks_5k_stats["longestStreakStart"]
                ),
                "longest5kStreakEnd": format_date(
                    streaks_5k_stats["longestStreakEnd"]
                ),
                "current5kStreak": streaks_5k_stats["currentStreak"],
                "current5kStreakStart": format_date(
                    streaks_5k_stats["currentStreakStart"]
                ),
                "current5kStreakEnd": format_date(
                    streaks_5k_stats["currentStreakEnd"]
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
    user_teams = load_user_teams()

    daily_steps_by_user = load_daily_steps_by_user(registered_users)

    daily_stats = calculate_daily_stats(
        daily_steps_by_user, last_fetch_date, registered_users
    )
    weekly_stats = calculate_weekly_stats(
        daily_steps_by_user,
        last_fetch_date,
        registered_users,
    )
    monthly_stats = calculate_monthly_stats(
        daily_steps_by_user,
        min(last_fetch_date, dt.date(2026, 11, 30)),
        registered_users,
    )
    streaks_5k_stats = calculate_5k_streaks_stats(
        daily_steps_by_user, last_fetch_date, registered_users
    )

    write_user_json_files(
        UserDataInputs(
            user_public_ids,
            user_teams,
            daily_steps_by_user,
            daily_stats,
            weekly_stats,
            monthly_stats,
            streaks_5k_stats,
        ),
        last_fetch,
        last_fetch_date,
    )
    write_leaderboard_json_file(
        daily_stats, weekly_stats, monthly_stats, streaks_5k_stats, last_fetch
    )


if __name__ == "__main__":
    main()
