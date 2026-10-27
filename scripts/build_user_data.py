"""Build per-user JSON data."""

import json
from pathlib import Path
from typing import cast


def load_user_public_ids() -> dict[str, str]:
    """Load user public IDs from the JSON file."""
    path = Path("..", "charlie-data", "data", "output", "user_public_ids.json")

    return cast(
        dict[str, str],
        json.loads(path.read_text(encoding="utf-8")),
    )


def main() -> None:
    """Main function."""
    load_user_public_ids()


if __name__ == "__main__":
    main()
