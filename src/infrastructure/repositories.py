from sqlalchemy.orm import Session

from domain.repositories import UserRepository, InventoryRepository, ScoreRepository
from domain.models import User, Inventory, Score

from .orm import UserORM, InventoryORM, ScoreORM



class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_name(self, user_name: str) -> User:
        user_orm = self.session.query(UserORM).filter_by(name=user_name).one()
        return User(
            id=user_orm.id,
            name=user_orm.name,
            password=user_orm.password
        )

class SqlAlchemyInventoryRepository(InventoryRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def get_inventory_by_user(self, user: User) -> Inventory:
        inventory_orm = self.session.query(InventoryORM).filter_by(user_id=user.id).one()
        return Inventory(
            id=inventory_orm.id,
            items=inventory_orm.items
        )

class SqlAlchemyScoreRepository(ScoreRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def get_score_by_user(self, user: User) -> Score:
        score_orm = self.session.query(ScoreORM).filter_by(user_id=user.id).one()
        return Score(
            id=score_orm.id,
            score=score_orm.score
        )