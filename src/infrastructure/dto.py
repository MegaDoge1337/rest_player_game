from pydantic import BaseModel


class User(BaseModel):
    name: str
    inventory: list[str]
    score: int


class Event(BaseModel):
    description: str
    user: User


class Action(BaseModel):
    action: str


class ActionResult(BaseModel):
    description: str
    inventory: list[str]
    score: int


class Token(BaseModel):
    access_token: str
    token_type: str
