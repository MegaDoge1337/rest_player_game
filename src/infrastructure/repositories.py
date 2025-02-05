from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from domain.repositories import UserRepository, InventoryRepository, ScoreRepository
from domain.models import User, Inventory, Score

from .orm import UserORM, InventoryORM, ScoreORM



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
            score=None
        )
    
    def create_user(self, user: User) -> User:
        user_orm = UserORM(
            name=user.name,
            password=user.password
        )
        self.session.add(user_orm)
        self.session.commit()
        user.id = user_orm.id
        return user


class SqlAlchemyInventoryRepository(InventoryRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def get_inventory_by_user(self, user: User) -> Inventory:
        inventory_orm = self.session.query(InventoryORM).filter_by(user_id=user.id).one()
        return Inventory(
            id=inventory_orm.id,
            items=inventory_orm.items
        )
    
    def create_user_invetory(self, user: User) -> Inventory:
        inventory_orm = InventoryORM(
            user_id=user.id,
            items=['Палка']
        )
        
        self.session.add(inventory_orm)
        self.session.commit()

        return Inventory(
            id=inventory_orm.id,
            items=inventory_orm.items
        )
    
    def update_user_invetory(self, user, items):
        return super().update_user_invetory(user, items)

class SqlAlchemyScoreRepository(ScoreRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def get_score_by_user(self, user: User) -> Score:
        score_orm = self.session.query(ScoreORM).filter_by(user_id=user.id).one()
        return Score(
            id=score_orm.id,
            score=score_orm.score
        )
    
    def create_user_score(self, user):
        score_orm = ScoreORM(
            score=1,
            user_id=user.id
        )

        self.session.add(score_orm)
        self.session.commit()

        return Score(
            id=score_orm.id,
            score=score_orm.score
        )
    
    def update_user_score(self, user, score):
        return super().update_user_score(user, score)