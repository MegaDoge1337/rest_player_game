from .models import User, Inventory, Score
from .repositories import ScoresRepository, InventoryRepository, UserRepository

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    def get_user_by_id(self, user_id: int) -> User:
        return self.repo.get_user_by_id(user_id)

class InventoryService:
    def __init__(self, repo: InventoryRepository):
        self.repo = repo

    def get_inventory_by_user(self, user: User) -> Inventory:
        return self.repo.get_inventory_by_user(user)

class ScoresService:
    def __init__(self, repo: ScoresRepository):
        self.repo = repo
    
    def get_score_by_user(self, user: User) -> Score:
        return self.repo.get_score_by_user(user)
