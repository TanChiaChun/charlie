from pathlib import Path

import pytest

import build_user_data


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
