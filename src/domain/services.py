from .models import ActionResult, Event, User, Token
from .repositories import (
    EventRepository,
    InventoryRepository,
    LLMRepository,
    ScoreRepository,
    UserRepository,
)
from .auth import Auth


class GameService:
    def __init__(
        self,
        auth: Auth,
        user_repo: UserRepository,
        inventory_repo: InventoryRepository,
        score_repo: ScoreRepository,
        event_repo: EventRepository,
        llm_repo: LLMRepository,
    ):
        self.auth = auth
        self.user_repo = user_repo
        self.inventory_repo = inventory_repo
        self.score_repo = score_repo
        self.event_repo = event_repo
        self.llm_repo = llm_repo

    def get_access_token(self, name: str, password: str) -> Token:
        user = self.user_repo.get_user_by_name(name)
        if not self.auth.authenticate_user(user, password):
            raise PermissionError("Incorrect user name or password")
        access_token = self.auth.create_access_token(data={"sub": user.name})
        return Token(token=access_token, type="bearer")

    def create_user(self, name: str, password: str) -> User:
        hashed_password = self.auth.get_password_hash(password)
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

    def get_current_user(self, token: str) -> User:
        user_name = self.auth.get_current_user_name(token)
        user = self.user_repo.get_user_by_name(user_name)
        if not user or not user_name:
            raise PermissionError("Incorrect user name or password")

        user.inventory = self.inventory_repo.get_inventory_by_user(user)
        user.score = self.score_repo.get_score_by_user(user)
        return user

    def make_action(self, action: str, token: str) -> ActionResult:
        user_name = self.auth.get_current_user_name(token)
        user = self.user_repo.get_user_by_name(user_name)
        if not user or not user_name:
            raise PermissionError("Incorrect user name or password")

        user.inventory = self.inventory_repo.get_inventory_by_user(user)
        user.score = self.score_repo.get_score_by_user(user)

        try:
            result = self.llm_repo.make_action(user, action)
        except ConnectionError as ex:
            raise ConnectionError(ex)
        except ValueError as ex:
            raise ValueError(ex)

        self.inventory_repo.update_user_invetory(user, result.inventory)
        self.score_repo.update_user_score(user, result.score)
        self.event_repo.create_event(result.description, user)
        return result

    def get_user_events(self, page: int, token: str) -> list[Event]:
        user_name = self.auth.get_current_user_name(token)
        user = self.user_repo.get_user_by_name(user_name)
        if not user or not user_name:
            raise PermissionError("Incorrect user name or password")

        user.inventory = self.inventory_repo.get_inventory_by_user(user)
        user.score = self.score_repo.get_score_by_user(user)

        return self.event_repo.get_user_events(user, page)

    def get_all_events(self, page: int, token: str) -> list[Event]:
        user_name = self.auth.get_current_user_name(token)
        user = self.user_repo.get_user_by_name(user_name)
        if not user or not user_name:
            raise PermissionError("Incorrect user name or password")

        return self.event_repo.get_all_events(page)

    def get_users_with_best_score(self, token: str) -> list[User]:
        user_name = self.auth.get_current_user_name(token)
        user = self.user_repo.get_user_by_name(user_name)
        if not user or not user_name:
            raise PermissionError("Incorrect user name or password")

        users = self.user_repo.get_users_list()
        for user in users:
            user.score = self.score_repo.get_score_by_user(user)
        users.sort(reverse=True, key=lambda x: x.score.score)
        return users
