"""Build per-user JSON data."""

import csv
import json
from pathlib import Path
from typing import cast

DATA_DIR = Path("..", "charlie-data", "data")


def load_user_daily_steps(
    registered_users: set[str],
) -> dict[str, dict[str, int]]:
    """Load daily steps for each registered user.

    Args:
        registered_users: Usernames to include.

    Returns:
        Mapping of usernames to daily steps, with dates as keys and step counts
        as values.
    """
    user_daily_steps: dict[str, dict[str, int]] = {}

    raw_data_dirs = sorted((DATA_DIR / "raw").iterdir())
    for raw_data_dir in raw_data_dirs:
        user_latest_steps = load_user_latest_steps(
            raw_data_dir, registered_users
        )
        for username, steps_by_date in user_latest_steps.items():
            user_daily_steps.setdefault(username, {}).update(steps_by_date)

    return user_daily_steps


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
                    username in registered_users
                    and username not in user_latest_steps
                ):
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


def main() -> None:
    """Main function."""
    load_user_public_ids()


if __name__ == "__main__":
    main()
