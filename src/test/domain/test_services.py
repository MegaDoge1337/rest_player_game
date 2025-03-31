from unittest.mock import create_autospec

import pytest

from src.domain.auth import Auth
from src.domain.models import ActionResult, Event, Inventory, Score, User
from src.domain.repositories import (
    EventRepository,
    InventoryRepository,
    LLMRepository,
    ScoreRepository,
    UserRepository,
)
from src.domain.services import GameService


def get_game_service():
    return GameService(
        auth=create_autospec(Auth),
        user_repo=create_autospec(UserRepository),
        inventory_repo=create_autospec(InventoryRepository),
        score_repo=create_autospec(ScoreRepository),
        event_repo=create_autospec(EventRepository),
        llm_repo=create_autospec(LLMRepository),
    )


def get_user(id: int, name: str, password: str) -> User:
    return User(id=id, name=name, password=password, inventory=None, score=None)


def get_user_inventory(id: int, items: list[str]) -> Inventory:
    return Inventory(id=id, items=items)


def get_user_score(id: int, score: int) -> Score:
    return Score(id=id, score=score)


def get_action(
    description: str, inventory: list[str], score: int, user: User
) -> ActionResult:
    return ActionResult(
        description=description, inventory=inventory, score=score, user=user
    )


def get_event(description: str, user: User):
    return Event(description=description, user=user)


@pytest.mark.parametrize(("id", "name", "password"), [(1, "username", "somepassword")])
def test_get_access_token_with_incorrect_credentials(id: int, name: str, password: str):
    game_service = get_game_service()

    user = get_user(id, name, password)

    game_service.user_repo.get_user_by_name.return_value = user
    game_service.auth.authenticate_user.return_value = None

    with pytest.raises(PermissionError):
        game_service.get_access_token(name, password)


@pytest.mark.parametrize(("id", "name", "password"), [(1, "username", "somepassword")])
def test_get_access_token(id: int, name: str, password: str):
    game_service = get_game_service()

    user = get_user(id, name, password)

    game_service.user_repo.get_user_by_name.return_value = user
    game_service.auth.authenticate_user.return_value = user
    game_service.auth.create_access_token.return_value = "token"

    token = game_service.get_access_token(name, password)

    assert token.token == "token"
    assert token.type == "bearer"


@pytest.mark.parametrize(
    (
        "id",
        "name",
        "password",
        "hashed_password",
        "inventory_id",
        "inventory_items",
        "score_id",
        "score_value",
    ),
    [(1, "username", "somepassword", "somehashedpassword", 1, ["item"], 1, 1)],
)
def test_create_user_when_not_exists(
    id: int,
    name: str,
    password: str,
    hashed_password: str,
    inventory_id: int,
    inventory_items: list[str],
    score_id: int,
    score_value: int,
):
    game_service = get_game_service()
    game_service.auth.get_password_hash.return_value = hashed_password
    game_service.user_repo.get_user_by_name.return_value = None
    game_service.user_repo.create_user.return_value = get_user(
        id, name, hashed_password
    )
    game_service.inventory_repo.create_user_invetory.return_value = get_user_inventory(
        inventory_id, inventory_items
    )
    game_service.score_repo.create_user_score.return_value = get_user_score(
        score_id, score_value
    )

    user = game_service.create_user(name, password)
    assert user.name == name
    assert user.password == hashed_password
    assert user.inventory.items == inventory_items
    assert user.score.score == score_value


@pytest.mark.parametrize(("id", "name", "password"), [(1, "username", "somepassword")])
def test_create_user_when_exists(id: int, name: str, password: str):
    game_service = get_game_service()
    game_service.auth.get_password_hash.return_value = "somehashedpassword"
    game_service.user_repo.get_user_by_name.return_value = get_user(id, name, password)

    with pytest.raises(ValueError):
        game_service.create_user(name, password)


@pytest.mark.parametrize(
    (
        "token",
        "id",
        "name",
        "hashed_password",
        "inventory_id",
        "inventory_items",
        "score_id",
        "score_value",
    ),
    [("sometoken", 1, "username", "somehashedpassword", 1, ["item"], 1, 1)],
)
def test_get_user_when_exists(
    token: str,
    id: int,
    name: str,
    hashed_password: str,
    inventory_id: int,
    inventory_items: list[str],
    score_id: int,
    score_value: int,
):
    game_service = get_game_service()

    game_service.auth.get_current_user_name.return_value = name
    game_service.user_repo.get_user_by_name.return_value = get_user(
        id, name, hashed_password
    )
    game_service.inventory_repo.get_inventory_by_user.return_value = get_user_inventory(
        inventory_id, inventory_items
    )
    game_service.score_repo.get_score_by_user.return_value = get_user_score(
        score_id, score_value
    )

    user = game_service.get_current_user(token)
    assert user.name == name
    assert user.inventory.items == inventory_items
    assert user.score.score == score_value


@pytest.mark.parametrize(("token"), ["sometoken"])
def test_get_user_when_credentials_incorrect(token: str):
    game_service = get_game_service()
    game_service.auth.get_current_user_name.return_value = None
    game_service.user_repo.get_user_by_name.return_value = None

    with pytest.raises(PermissionError):
        game_service.get_current_user(token)


@pytest.mark.parametrize(
    ("token", "id", "name", "action_description", "action_inventory", "action_score"),
    [("sometoken", 1, "username", "somedescription", ["new_item"], 10)],
)
def test_make_action(
    token: str,
    id: int,
    name: str,
    action_description: str,
    action_inventory: str,
    action_score: int,
):
    game_service = get_game_service()

    user = get_user(id, name, None)
    action = get_action(action_description, action_inventory, action_score, user)

    game_service.auth.get_current_user_name.return_value = name
    game_service.user_repo.get_user_by_name.return_value = user
    game_service.llm_repo.make_action.return_value = action
    game_service.inventory_repo.update_user_invetory.return_value = None
    game_service.score_repo.update_user_score.return_value = None
    game_service.event_repo.create_event.return_value = None

    result = game_service.make_action(action_description, token)

    assert result.description == action_description
    assert result.inventory == action_inventory
    assert result.score == action_score
    assert result.user.id == user.id
    assert result.user.name == user.name


@pytest.mark.parametrize(
    ("token", "id", "name", "action_description"),
    [("sometoken", 1, "username", "somedescription")],
)
def test_make_action_when_connection_failed(
    token: str, id: int, name: str, action_description: str
):
    user = get_user(id, name, None)

    game_service = get_game_service()
    game_service.auth.get_current_user_name.return_value = name
    game_service.user_repo.get_user_by_name.return_value = user
    game_service.llm_repo.make_action.side_effect = ConnectionError("Connection error.")

    with pytest.raises(ConnectionError):
        game_service.make_action(action_description, token)


@pytest.mark.parametrize(
    ("token", "id", "name", "action_description"),
    [("sometoken", 1, "username", "somedescription")],
)
def test_make_action_when_json_load_failed(
    token: str, id: int, name: str, action_description: str
):
    user = get_user(id, name, None)

    game_service = get_game_service()
    game_service.auth.get_current_user_name.return_value = name
    game_service.user_repo.get_user_by_name.return_value = user
    game_service.llm_repo.make_action.side_effect = ValueError("Value error.")

    with pytest.raises(ValueError):
        game_service.make_action(action_description, token)


@pytest.mark.parametrize(
    ("token", "action_description"), [("sometoken", "somedescription")]
)
def test_make_action_when_credentials_incorrect(token: str, action_description: str):
    game_service = get_game_service()
    game_service.auth.get_current_user_name.return_value = None
    game_service.user_repo.get_user_by_name.return_value = None

    with pytest.raises(PermissionError):
        game_service.make_action(action_description, token)


@pytest.mark.parametrize(
    ("token", "id", "name", "event_description", "page"),
    [("sometoken", 1, "username", "someevent", 0)],
)
def test_get_user_events(
    token: str, id: int, name: str, event_description: str, page: int
):
    game_service = get_game_service()

    user = get_user(id, name, None)
    event = get_event(event_description, user)

    game_service.auth.get_current_user_name.return_value = name
    game_service.user_repo.get_user_by_name.return_value = user
    game_service.event_repo.get_user_events.return_value = [event]

    events = game_service.get_user_events(page, token)

    assert events[0].description == event.description
    assert events[0].user.id == event.user.id
    assert events[0].user.name == event.user.name


@pytest.mark.parametrize(("token", "page"), [("sometoken", 0)])
def test_get_user_events_when_credentials_incorrect(token: str, page: int):
    game_service = get_game_service()

    game_service.auth.get_current_user_name.return_value = None
    game_service.user_repo.get_user_by_name.return_value = None

    with pytest.raises(PermissionError):
        game_service.get_user_events(page, token)


@pytest.mark.parametrize(
    ("token", "id", "name", "event_description", "page"),
    [("sometoken", 1, "username", "someevent", 0)],
)
def test_get_all_events(
    token: str, id: int, name: str, event_description: str, page: int
):
    game_service = get_game_service()

    user = get_user(id, name, None)
    event = get_event(event_description, user)

    game_service.auth.get_current_user_name.return_value = name
    game_service.user_repo.get_user_by_name.return_value = user
    game_service.event_repo.get_all_events.return_value = [event]

    events = game_service.get_all_events(page, token)

    assert events[0].description == event.description
    assert events[0].user.id == event.user.id
    assert events[0].user.name == event.user.name


@pytest.mark.parametrize(("token", "page"), [("sometoken", 0)])
def test_get_all_events_when_credentials_incorrect(token: str, page: int):
    game_service = get_game_service()

    game_service.auth.get_current_user_name.return_value = None
    game_service.user_repo.get_user_by_name.return_value = None

    with pytest.raises(PermissionError):
        game_service.get_all_events(page, token)


@pytest.mark.parametrize(
    ("token", "id", "name", "score_id", "score_value"),
    [("sometoken", 1, "username", 1, 1)],
)
def test_get_users_with_best_score(
    token: str, id: int, name: str, score_id: int, score_value: int
):
    game_service = get_game_service()

    user = get_user(id, name, None)
    score = get_user_score(score_id, score_value)

    game_service.auth.get_current_user_name.return_value = name
    game_service.user_repo.get_user_by_name.return_value = user
    game_service.user_repo.get_users_list.return_value = [user]
    game_service.score_repo.get_score_by_user.return_value = score

    users = game_service.get_users_with_best_score(token)

    assert users[0].id == id
    assert users[0].name == name
    assert users[0].score.id == score_id
    assert users[0].score.score == score_value


@pytest.mark.parametrize(("token"), ["sometoken"])
def test_get_users_with_best_score_when_credentials_incorrect(token: str):
    game_service = get_game_service()

    game_service.auth.get_current_user_name.return_value = None
    game_service.user_repo.get_user_by_name.return_value = None

    with pytest.raises(PermissionError):
        game_service.get_users_with_best_score(token)
