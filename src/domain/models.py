from dataclasses import dataclass

@dataclass
class Score:
    id: int
    score: int

@dataclass
class Inventory:
    id: int
    items: list[str]

@dataclass
class User:
    id: int
    name: str
    password: str
    inventory: Inventory
    score: Score

@dataclass
class ActionResult:
    description: str
    user: User

@dataclass
class Event:
    description: str
    user: User