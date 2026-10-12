"""Aggregate users' daily steps from raw CSV files."""

import csv
from pathlib import Path


def load_users() -> set[str]:
    """Load users from the users CSV file."""
    with open(
        Path("..", "charlie-data", "data", "input", "users.csv"), newline=""
    ) as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        return {username for [username] in csv_reader}


def load_user_latest_steps(raw_data_dir: Path) -> dict[str, dict[str, int]]:
    """Load the latest available steps for each user.

    Args:
        raw_data_dir: Directory containing raw CSV files.

    Returns:
        Mapping of usernames to their latest steps, with dates as keys and step
        counts as values.
    """
    csv_paths = sorted(raw_data_dir.iterdir(), reverse=True)

    user_latest_steps = {}
    for csv_path in csv_paths:
        with open(csv_path, newline="") as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for username, steps, date in csv_reader:
                if username not in user_latest_steps:
                    user_latest_steps[username] = {date: int(steps)}

    return user_latest_steps


def main() -> None:
    """Main function."""
    load_users()


if __name__ == "__main__":
    main()
