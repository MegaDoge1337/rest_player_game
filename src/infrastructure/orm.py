from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, JSON, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    inventory = relationship('InventoryORM', backref='user', uselist=False)
    score = relationship('ScoreORM', backref='user', uselist=False)
    events = relationship("EventORM")

class InventoryORM(Base):
    __tablename__ = "inventories"
    id = Column(Integer, primary_key=True)
    items = Column(JSON)
    user_id = Column(Integer, ForeignKey('users.id')) 

class ScoreORM(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True)
    score = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))

class EventORM(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    description = Column(Text)
    timestamp = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))


