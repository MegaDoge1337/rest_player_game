import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.orm import Base, UserORM, InventoryORM, ScoreORM, EventORM

DATABASE_URL = "sqlite:///:memory:"


def get_session():
    engine = create_engine(DATABASE_URL)
    SessionFactory = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return SessionFactory()


@pytest.mark.parametrize(("name", "password"), [("username", "1Qwerty")])
def test_create_get_user(name: str, password: str):
    session = get_session()

    user_orm = UserORM(name=name, password=password)

    session.add(user_orm)
    session.commit()

    user_orm = session.query(UserORM).filter_by(id=user_orm.id).one()

    assert user_orm.name == name
    assert user_orm.password == password

    session.query(UserORM).filter_by(id=user_orm.id).delete()
    session.commit()


@pytest.mark.parametrize(("items"), [["item"]])
def test_create_get_inventory(items: list[str]):
    session = get_session()

    inventory_orm = InventoryORM(items=items, user_id=0)

    session.add(inventory_orm)
    session.commit()

    inventory_orm = session.query(InventoryORM).filter_by(id=inventory_orm.id).one()

    assert inventory_orm.items[0] == items[0]

    session.query(InventoryORM).filter_by(id=inventory_orm.id).delete()
    session.commit()


@pytest.mark.parametrize(("score"), [1])
def test_create_get_score(score: int):
    session = get_session()

    score_orm = ScoreORM(score=score, user_id=0)

    session.add(score_orm)
    session.commit()

    score_orm = session.query(ScoreORM).filter_by(id=score_orm.id).one()

    assert score_orm.score == score

    session.query(ScoreORM).filter_by(id=score_orm.id).delete()
    session.commit()


@pytest.mark.parametrize(("description"), ["somedescription"])
def test_create_get_event(description: str):
    session = get_session()

    event_orm = EventORM(description=description, user_id=0)

    session.add(event_orm)
    session.commit()

    event_orm = session.query(EventORM).filter_by(id=event_orm.id).one()

    assert event_orm.description == description

    session.query(EventORM).filter_by(id=event_orm.id).delete()
    session.commit()


@pytest.mark.parametrize(
    ("user_name", "user_password", "items"), [("username", "1Qwerty", ["item"])]
)
def test_user_invenotry_relation(user_name: str, user_password: str, items: list[str]):
    session = get_session()

    user_orm = UserORM(name=user_name, password=user_password)

    session.add(user_orm)
    session.commit()

    inventory_orm = InventoryORM(items=items, user_id=user_orm.id)

    session.add(inventory_orm)
    session.commit()

    user_orm = session.query(UserORM).filter_by(id=user_orm.id).one()
    inventory_orm = session.query(InventoryORM).filter_by(id=inventory_orm.id).one()

    assert user_orm.inventory.items[0] == inventory_orm.items[0]
    assert inventory_orm.user.name == user_orm.name
    assert inventory_orm.user.password == user_orm.password

    session.query(InventoryORM).filter_by(id=inventory_orm.id).delete()
    session.query(UserORM).filter_by(id=user_orm.id).delete()
    session.commit()


@pytest.mark.parametrize(
    ("user_name", "user_password", "score"), [("username", "1Qwerty", 1)]
)
def test_user_score_relation(user_name: str, user_password: str, score: int):
    session = get_session()

    user_orm = UserORM(name=user_name, password=user_password)

    session.add(user_orm)
    session.commit()

    score_orm = ScoreORM(score=score, user_id=user_orm.id)

    session.add(score_orm)
    session.commit()

    user_orm = session.query(UserORM).filter_by(id=user_orm.id).one()
    score_orm = session.query(ScoreORM).filter_by(id=score_orm.id).one()

    assert user_orm.score.score == score_orm.score
    assert score_orm.user.name == user_orm.name
    assert score_orm.user.password == user_orm.password

    session.query(ScoreORM).filter_by(id=score_orm.id).delete()
    session.query(UserORM).filter_by(id=user_orm.id).delete()
    session.commit()


@pytest.mark.parametrize(
    ("user_name", "user_password", "description"),
    [("username", "1Qwerty", "somedescription")],
)
def test_user_event_relation(user_name: str, user_password: str, description: str):
    session = get_session()

    user_orm = UserORM(name=user_name, password=user_password)

    session.add(user_orm)
    session.commit()

    event_orm = EventORM(description=description, user_id=user_orm.id)

    session.add(event_orm)
    session.commit()

    user_orm = session.query(UserORM).filter_by(id=user_orm.id).one()
    event_orm = session.query(EventORM).filter_by(id=event_orm.id).one()

    assert user_orm.events[0].description == event_orm.description
    assert event_orm.user.name == user_orm.name
    assert event_orm.user.password == user_orm.password

    session.query(EventORM).filter_by(id=event_orm.id).delete()
    session.query(UserORM).filter_by(id=user_orm.id).delete()
    session.commit()
