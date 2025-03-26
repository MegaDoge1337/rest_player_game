from .models import Action, Event, User
from .repositories import (
    EventRepository,
    InventoryRepository,
    LLMRepository,
    ScoreRepository,
    UserRepository,
)


class GameService:
    def __init__(
        self,
        user_repo: UserRepository,
        inventory_repo: InventoryRepository,
        score_repo: ScoreRepository,
        event_repo: EventRepository,
        llm_repo: LLMRepository,
    ):
        self.user_repo = user_repo
        self.inventory_repo = inventory_repo
        self.score_repo = score_repo
        self.event_repo = event_repo
        self.llm_repo = llm_repo

    def create_user(self, name: str, hashed_password: str) -> User:
        user = self.user_repo.get_user_by_name(name)
        if user:
            raise ValueError(f"User with name {name} already exists")
        user = User(
            id=None, name=name, password=hashed_password, inventory=None, score=None
        )
        user = self.user_repo.create_user(user)
        user.inventory = self.inventory_repo.create_user_invetory(user)
        user.score = self.score_repo.create_user_score(user)
        return user

    def get_user(self, name: str) -> User:
        user = self.user_repo.get_user_by_name(name)

        if not user:
            return None

        user.inventory = self.inventory_repo.get_inventory_by_user(user)
        user.score = self.score_repo.get_score_by_user(user)
        return user

    def make_action(self, user: User, action: str) -> Action:
        result = self.llm_repo.make_action(user, action)

        if not result:
            return None

        self.inventory_repo.update_user_invetory(user, result.inventory)
        self.score_repo.update_user_score(user, result.score)
        return result

    def write_event(self, user: User, description: str) -> Event:
        return self.event_repo.create_event(description, user)

    def get_user_events(self, user: User, page: int) -> list[Event]:
        return self.event_repo.get_user_events(user, page)

    def get_all_events(self, page: int) -> list[Event]:
        return self.event_repo.get_all_events(page)

    def get_users_with_best_score(self) -> list[User]:
        users = self.user_repo.get_users_list()
        for user in users:
            user.score = self.score_repo.get_score_by_user(user)
        users.sort(reverse=True, key=lambda x: x.score.score)
        return users
