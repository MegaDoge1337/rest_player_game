import pytest
from unittest.mock import create_autospec

from src.domain.models import User, Inventory, Score
from src.domain.repositories import (
    UserRepository,
    InventoryRepository,
    ScoreRepository,
    EventRepository,
    LLMRepository
)
from src.domain.services import GameService

def get_game_service():
    return GameService(
        user_repo=create_autospec(UserRepository),
        inventory_repo=create_autospec(InventoryRepository),
        score_repo=create_autospec(ScoreRepository),
        event_repo=create_autospec(EventRepository),
        llm_repo=create_autospec(LLMRepository)
    )

def get_user(id: int, name: str, hashed_password: str) -> User:
    return User(
        id=id,
        name=name,
        password=hashed_password,
        inventory=None,
        score=None
    )

def get_user_inventory(id: int, items: list[str]) -> Inventory:
    return Inventory(
        id=id,
        items=items
    )

def get_user_score(id: int, score: int) -> Score:
    return Score(
        id=id,
        score=score
    )

@pytest.mark.parametrize(
    ("id", "name", "hashed_password"),
    [
        (1, "username", "somehashedpassword")
    ]
)
def test_create_user_when_exists(id: int, name: str, hashed_password: str):
    game_service = get_game_service()
    game_service.user_repo.get_user_by_name.return_value = get_user(id, name, hashed_password)

    with pytest.raises(ValueError):
        game_service.create_user(name, hashed_password)

@pytest.mark.parametrize(
    ("id", "name", "hashed_password", "inventory_id", "inventory_items", "score_id", "score_value"),
    [
        (1, "username", "somehashedpassword", 1, ["item"], 1, 1)
    ]
)
def test_create_user_when_not_exists(id: int, name: str, hashed_password: str, inventory_id: int, inventory_items: list[str], score_id: int, score_value: int):
    game_service = get_game_service()
    game_service.user_repo.get_user_by_name.return_value = None
    game_service.user_repo.create_user.return_value = get_user(id, name, hashed_password)
    game_service.inventory_repo.create_user_invetory.return_value = get_user_inventory(inventory_id, inventory_items)
    game_service.score_repo.create_user_score.return_value = get_user_score(score_id, score_value)

    user = game_service.create_user(name, hashed_password)
    assert user.name == name
    assert user.password == hashed_password
    assert user.inventory.items == inventory_items
    assert user.score.score == score_value

@pytest.mark.parametrize(
    ("id", "name", "hashed_password", "inventory_id", "inventory_items", "score_id", "score_value"),
    [
        (1, "username", "somehashedpassword", 1, ["item"], 1, 1)
    ]
)
def test_get_user_when_exists(id: int, name: str, hashed_password: str, inventory_id: int, inventory_items: list[str], score_id: int, score_value: int):
    game_service = get_game_service()
    game_service.user_repo.get_user_by_name.return_value = get_user(id, name, hashed_password)
    game_service.inventory_repo.get_inventory_by_user.return_value = get_user_inventory(inventory_id, inventory_items)
    game_service.score_repo.get_score_by_user.return_value = get_user_score(score_id, score_value)

    user = game_service.get_user(name)
    assert user.name == name
    assert user.inventory.items == inventory_items
    assert user.score.score == score_value

@pytest.mark.parametrize(
    ("name"),
    [
        ("username")
    ]
)
def test_get_user_when_not_exists(name: str):
    game_service = get_game_service()
    game_service.user_repo.get_user_by_name.return_value = None

    user = game_service.get_user(name)
    assert user is None