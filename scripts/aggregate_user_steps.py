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


def main() -> None:
    """Main function."""
    load_users()


if __name__ == "__main__":
    main()
