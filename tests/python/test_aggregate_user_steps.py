import aggregate_user_steps
from pytest_mock import MockerFixture


def test_load_users(mocker: MockerFixture) -> None:
    mocker.patch(
        "aggregate_user_steps.open",
        mocker.mock_open(read_data="username\nuser1\nuser2"),
    )
    assert aggregate_user_steps.load_users() == {"user1", "user2"}
