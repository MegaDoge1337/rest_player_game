from .models import User, Action
from .repositories import ScoreRepository, InventoryRepository, UserRepository, LLMRepository

class GameService:
    def __init__(self, 
                 user_repo: UserRepository,
                 inventory_repo: InventoryRepository,
                 score_repo: ScoreRepository,
                 llm_repo: LLMRepository):
        self.user_repo = user_repo
        self.inventory_repo = inventory_repo
        self.score_repo = score_repo
        self.llm_repo = llm_repo
    
    def create_user(self, name: str, hashed_password: str) -> User:
        user = self.user_repo.get_user_by_name(name)
        if user:
            raise ValueError(f"User with name {name} already exists")
        user = User(
            id=None,
            name=name, 
            password=hashed_password,
            inventory=None,
            score=None
        )
        user = self.user_repo.create_user(user)
        user.inventory = self.inventory_repo.create_user_invetory(user)
        user.score = self.score_repo.create_user_score(user)
        return user
    
    def get_user(self, name: str) -> User:
        user = self.user_repo.get_user_by_name(name)
        user.inventory = self.inventory_repo.get_inventory_by_user(user)
        user.score = self.score_repo.get_score_by_user(user)
        return user

    def make_action(self, user: User, action: str):
        result = self.llm_repo.make_action(action)
        self.inventory_repo.update_user_invetory(user, result["inventory"])
        self.score_repo.update_user_score(user, result["score"])

        return Action(
            result=result["result"],
            inventory=result["inventory"],
            score=(result["score"] + user.score)
        )