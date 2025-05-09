import json
import os
import random

from openai import APIConnectionError, OpenAI
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from domain.models import ActionResult, Event, Inventory, Score, User
from domain.repositories import (
    EventRepository,
    InventoryRepository,
    LLMRepository,
    ScoreRepository,
    UserRepository,
)

from .llm import ACTION_PROMPT_TEMPATE, SYSTEM_PROMPT
from .orm import EventORM, InventoryORM, ScoreORM, UserORM


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_name(self, user_name: str) -> User:
        try:
            user_orm = self.session.query(UserORM).filter_by(name=user_name).one()
        except NoResultFound:
            return None

        return User(
            id=user_orm.id,
            name=user_orm.name,
            password=user_orm.password,
            inventory=None,
            score=None,
        )

    def get_users_list(self) -> list[User]:
        user_orms = self.session.query(UserORM).all()

        return [
            User(
                id=user_orm.id,
                name=user_orm.name,
                password=user_orm.password,
                inventory=None,
                score=None,
            )
            for user_orm in user_orms
        ]

    def create_user(self, user: User) -> User:
        user_orm = UserORM(name=user.name, password=user.password)
        self.session.add(user_orm)
        self.session.commit()
        user.id = user_orm.id
        return user


class SqlAlchemyInventoryRepository(InventoryRepository):
    def __init__(self, session: Session):
        self.session = session
        self.default_inventory = os.environ.get(
            "DEFAULT_INVENTORY", "Камень,Палка"
        ).split(",")

    def get_inventory_by_user(self, user: User) -> Inventory:
        try:
            inventory_orm = (
                self.session.query(InventoryORM).filter_by(user_id=user.id).one()
            )
        except NoResultFound:
            return None

        return Inventory(id=inventory_orm.id, items=inventory_orm.items)

    def create_user_invetory(self, user: User) -> Inventory:
        inventory_orm = InventoryORM(user_id=user.id, items=self.default_inventory)

        self.session.add(inventory_orm)
        self.session.commit()

        return Inventory(id=inventory_orm.id, items=inventory_orm.items)

    def update_user_invetory(self, user, items) -> Inventory:
        try:
            inventory_orm = (
                self.session.query(InventoryORM).filter_by(user_id=user.id).one()
            )
        except NoResultFound:
            return None

        inventory_orm.items = items

        self.session.add(inventory_orm)
        self.session.commit()

        return Inventory(id=inventory_orm.id, items=inventory_orm.items)


class SqlAlchemyScoreRepository(ScoreRepository):
    def __init__(self, session: Session):
        self.session = session
        self.default_score = int(os.environ.get("DEFAULT_SCORE", "1"))

    def get_score_by_user(self, user: User) -> Score:
        try:
            score_orm = self.session.query(ScoreORM).filter_by(user_id=user.id).one()
        except NoResultFound:
            return None

        return Score(id=score_orm.id, score=score_orm.score)

    def create_user_score(self, user):
        score_orm = ScoreORM(user_id=user.id, score=self.default_score)

        self.session.add(score_orm)
        self.session.commit()

        return Score(id=score_orm.id, score=score_orm.score)

    def update_user_score(self, user, score):
        try:
            score_orm = self.session.query(ScoreORM).filter_by(user_id=user.id).one()
        except NoResultFound:
            return None

        score_orm.score = score_orm.score + score

        if score_orm.score < 0:
            score_orm.score = 0

        self.session.add(score_orm)
        self.session.commit()

        return Score(id=score_orm.id, score=score_orm.score)


class SqlAlchemyEventRepository(EventRepository):
    def __init__(self, session: Session):
        self.session = session
        self.page_size = int(os.environ.get("EVENTS_PAGE_LIMIT", "3"))

    def create_event(self, description: str, user: User):
        event_orm = EventORM(user_id=user.id, description=description)

        self.session.add(event_orm)
        self.session.commit()

        return Event(description=description, user=user)

    def get_user_events(self, user: User, page: int) -> list[Event]:
        event_orms = (
            self.session.query(EventORM)
            .filter_by(user_id=user.id)
            .limit(self.page_size)
            .offset(self.page_size * page)
            .all()
        )
        events = [Event(event_orm.description, user) for event_orm in event_orms]
        return events

    def get_all_events(self, page: int) -> list[Event]:
        event_orms = (
            self.session.query(EventORM)
            .limit(self.page_size)
            .offset(self.page_size * page)
            .all()
        )
        events = [
            Event(
                description=event_orm.description,
                user=User(
                    id=event_orm.user.id,
                    name=event_orm.user.name,
                    password=None,
                    inventory=Inventory(
                        id=event_orm.user.inventory.id,
                        items=event_orm.user.inventory.items,
                    ),
                    score=Score(
                        id=event_orm.user.score.id, score=event_orm.user.score.score
                    ),
                ),
            )
            for event_orm in event_orms
        ]
        return events


class OpenAILLMRepository(LLMRepository):
    def __init__(self):
        self.base_url = os.environ.get("LLM_BASE_URL", "http://localhost:1234/v1")
        self.api_key = os.environ.get("LLM_API_KEY", "lm-studio")
        self.model = os.environ.get("LLM_MODEL", "aya-23-8b")
        self.temp = float(os.environ.get("LLM_TEMP", "0.7"))
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def make_action(self, user: User, action: str) -> ActionResult:
        user_action = ACTION_PROMPT_TEMPATE.format(
            action=action,
            inventory=", ".join(user.inventory.items),
            is_lucky=("не повезет" if random.randint(1, 20) < 10 else "повезет"),
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_action},
                ],
                temperature=self.temp,
            )
        except APIConnectionError as ex:
            raise ConnectionError(ex)

        try:
            completion_text = completion.choices[0].message.content
            completion_text = completion_text.replace("```json", "").replace("```", "")
            completion_text = completion_text.strip().rstrip()
            completion_json: dict[str, str] = json.loads(completion_text)
        except json.JSONDecodeError as ex:
            return ValueError(ex)

        return ActionResult(
            description=completion_json.get("result"),
            inventory=completion_json.get("inventory"),
            score=int(completion_json.get("score")),
            user=user,
        )
