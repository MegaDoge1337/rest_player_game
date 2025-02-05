from dataclasses import dataclass


@dataclass
class Score:
    id: int
    score: int


@dataclass
class Inventory:
    id: int
    items: list[str]

    def has_item(self, item: str) -> bool:
        return item in self.items


@dataclass
class User:
    id: int
    name: str
    password: str
    inventory: Inventory
    score: Score

    def get_inventory(self) -> list[str]:
        return self.inventory.items
    
    def has_item(self, item: str) -> bool:
        return self.inventory.has_item(item)

    def get_score(self) -> int:
        return self.score.score
