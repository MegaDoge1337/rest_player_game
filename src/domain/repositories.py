from abc import ABC, abstractmethod

from .models import ActionResult, Event, Inventory, Score, User


class ScoreRepository(ABC):
    @abstractmethod
    def get_score_by_user(self, user: User) -> Score:
        pass

    @abstractmethod
    def create_user_score(self, user: User) -> Score:
        pass

    @abstractmethod
    def update_user_score(self, user: User, score: int) -> Score:
        pass


class InventoryRepository(ABC):
    @abstractmethod
    def get_inventory_by_user(self, user: User) -> Inventory:
        pass

    @abstractmethod
    def create_user_invetory(self, user: User) -> Inventory:
        pass

    @abstractmethod
    def update_user_invetory(self, user: User, items: list[str]) -> Inventory:
        pass


class UserRepository(ABC):
    @abstractmethod
    def get_user_by_name(self, user_name: str) -> User:
        pass

    @abstractmethod
    def get_users_list(self) -> list[User]:
        pass

    @abstractmethod
    def create_user(self, user: User) -> User:
        pass


class EventRepository(ABC):
    @abstractmethod
    def create_event(self, description: str, user: User) -> Event:
        pass

    @abstractmethod
    def get_user_events(self, user: User, page: int) -> list[Event]:
        pass

    @abstractmethod
    def get_all_events(self, page: int) -> list[Event]:
        pass


class LLMRepository(ABC):
    @abstractmethod
    def make_action(self, user: User, action: str) -> ActionResult:
        pass
