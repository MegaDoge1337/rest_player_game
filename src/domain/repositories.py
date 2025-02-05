from abc import ABC, abstractmethod
from .models import Score, Inventory, User

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
    def create_user(self, name: str, password: str) -> User:
        pass
