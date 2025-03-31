from abc import ABC, abstractmethod
from .models import User


class Auth(ABC):
    @abstractmethod
    def get_password_hash(self, password: str) -> str:
        pass

    @abstractmethod
    def verify_pasword(self, plain_password: str, hashed_password: str) -> bool:
        pass

    @abstractmethod
    def authenticate_user(self, user: User, password: str) -> User:
        pass

    @abstractmethod
    def create_access_token(self, data: dict) -> str:
        pass

    @abstractmethod
    def get_current_user_name(self, token: str) -> str:
        pass
