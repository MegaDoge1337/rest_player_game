from abc import ABC, abstractmethod
from .models import Score, Inventory, User

class ScoresRepository(ABC):
    @abstractmethod
    def get_score_by_user(user: User) -> Score:
        pass

class InventoryRepository(ABC):
    @abstractmethod
    def get_inventory_by_user(user: User) -> Inventory:
        pass

class UserRepository(ABC):
    @abstractmethod
    def get_user_by_id(user_id: int) -> User:
        pass
