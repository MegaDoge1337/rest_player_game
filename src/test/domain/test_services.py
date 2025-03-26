from unittest.mock import create_autospec

import pytest

from src.domain.models import Action, Event, Inventory, Score, User
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
        user_repo=create_autospec(UserRepository),
        inventory_repo=create_autospec(InventoryRepository),
        score_repo=create_autospec(ScoreRepository),
        event_repo=create_autospec(EventRepository),
        llm_repo=create_autospec(LLMRepository),
    )


def get_user(id: int, name: str, hashed_password: str) -> User:
    return User(id=id, name=name, password=hashed_password, inventory=None, score=None)


def get_user_inventory(id: int, items: list[str]) -> Inventory:
    return Inventory(id=id, items=items)


def get_user_score(id: int, score: int) -> Score:
    return Score(id=id, score=score)


def get_action(
    description: str, inventory: list[str], score: int, user: User
) -> Action:
    return Action(description=description, inventory=inventory, score=score, user=user)


def get_event(description: str, user: User):
    return Event(description=description, user=user)


@pytest.mark.parametrize(
    ("id", "name", "hashed_password"), [(1, "username", "somehashedpassword")]
)
def test_create_user_when_exists(id: int, name: str, hashed_password: str):
    game_service = get_game_service()
    game_service.user_repo.get_user_by_name.return_value = get_user(
        id, name, hashed_password
    )

    with pytest.raises(ValueError):
        game_service.create_user(name, hashed_password)


@pytest.mark.parametrize(
    (
        "id",
        "name",
        "hashed_password",
        "inventory_id",
        "inventory_items",
        "score_id",
        "score_value",
    ),
    [(1, "username", "somehashedpassword", 1, ["item"], 1, 1)],
)
def test_create_user_when_not_exists(
    id: int,
    name: str,
    hashed_password: str,
    inventory_id: int,
    inventory_items: list[str],
    score_id: int,
    score_value: int,
):
    game_service = get_game_service()
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

    user = game_service.create_user(name, hashed_password)
    assert user.name == name
    assert user.password == hashed_password
    assert user.inventory.items == inventory_items
    assert user.score.score == score_value


@pytest.mark.parametrize(
    (
        "id",
        "name",
        "hashed_password",
        "inventory_id",
        "inventory_items",
        "score_id",
        "score_value",
    ),
    [(1, "username", "somehashedpassword", 1, ["item"], 1, 1)],
)
def test_get_user_when_exists(
    id: int,
    name: str,
    hashed_password: str,
    inventory_id: int,
    inventory_items: list[str],
    score_id: int,
    score_value: int,
):
    game_service = get_game_service()
    game_service.user_repo.get_user_by_name.return_value = get_user(
        id, name, hashed_password
    )
    game_service.inventory_repo.get_inventory_by_user.return_value = get_user_inventory(
        inventory_id, inventory_items
    )
    game_service.score_repo.get_score_by_user.return_value = get_user_score(
        score_id, score_value
    )

    user = game_service.get_user(name)
    assert user.name == name
    assert user.inventory.items == inventory_items
    assert user.score.score == score_value


@pytest.mark.parametrize(("name"), ["username"])
def test_get_user_when_not_exists(name: str):
    game_service = get_game_service()
    game_service.user_repo.get_user_by_name.return_value = None

    user = game_service.get_user(name)
    assert user is None


@pytest.mark.parametrize(
    ("id", "name", "action_description", "action_inventory", "action_score"),
    [(1, "username", "somedescription", ["new_item"], 10)],
)
def test_make_action(
    id: int,
    name: str,
    action_description: str,
    action_inventory: str,
    action_score: int,
):
    game_service = get_game_service()

    user = get_user(id, name, None)
    action = get_action(action_description, action_inventory, action_score, user)

    game_service.llm_repo.make_action.return_value = action
    game_service.inventory_repo.update_user_invetory.return_value = None
    game_service.score_repo.update_user_score.return_value = None

    result = game_service.make_action(user=user, action=action_description)

    assert result.description == action_description
    assert result.inventory == action_inventory
    assert result.score == action_score
    assert result.user.id == user.id
    assert result.user.name == user.name


@pytest.mark.parametrize(
    ("id", "name", "action_description"), [(1, "username", "somedescription")]
)
def test_make_action_when_failed(id: int, name: str, action_description: str):
    game_service = get_game_service()

    user = get_user(id, name, None)

    game_service.llm_repo.make_action.return_value = None

    result = game_service.make_action(user=user, action=action_description)

    assert result is None


@pytest.mark.parametrize(
    ("id", "name", "event_description"), [(1, "username", "someevent")]
)
def test_write_event(id: int, name: str, event_description: str):
    game_service = get_game_service()

    user = get_user(id, name, None)
    event = get_event(event_description, user)

    game_service.event_repo.create_event.return_value = event

    saved_event = game_service.write_event(user, event_description)

    assert saved_event.description == event.description
    assert saved_event.user.id == event.user.id
    assert saved_event.user.name == event.user.name


@pytest.mark.parametrize(
    ("id", "name", "event_description", "page"), [(1, "username", "someevent", 0)]
)
def test_get_user_events(id: int, name: str, event_description: str, page: int):
    game_service = get_game_service()

    user = get_user(id, name, None)
    event = get_event(event_description, user)

    game_service.event_repo.get_user_events.return_value = [event]

    events = game_service.get_user_events(user, page)

    assert events[0].description == event.description
    assert events[0].user.id == event.user.id
    assert events[0].user.name == event.user.name


@pytest.mark.parametrize(
    ("id", "name", "event_description", "page"), [(1, "username", "someevent", 0)]
)
def test_get_all_events(id: int, name: str, event_description: str, page: int):
    game_service = get_game_service()

    user = get_user(id, name, None)
    event = get_event(event_description, user)

    game_service.event_repo.get_all_events.return_value = [event]

    events = game_service.get_all_events(page)

    assert events[0].description == event.description
    assert events[0].user.id == event.user.id
    assert events[0].user.name == event.user.name
