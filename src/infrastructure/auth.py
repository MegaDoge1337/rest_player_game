import os
from datetime import datetime, timedelta

import jwt

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from domain.models import User
from domain.auth import Auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class JwtAuth(Auth):
    def __init__(self):
        self.secret_key = os.environ.get("SECRET_KEY")

        if not self.secret_key:
            raise ValueError("Environment variable `SECRET_KEY` not defined.")

        self.algorithm = os.environ.get("ALGORITHM")

        if not self.algorithm:
            raise ValueError("Environment variable `ALGORITHM` not defined.")

        self.access_token_expires = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_pasword(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self, user: User, password: str) -> User:
        if not user or not self.verify_pasword(password, user.password):
            return None
        return user

    def create_access_token(self, data: dict) -> str:
        expires_delta = timedelta(minutes=self.access_token_expires)
        to_encode = data.copy()
        expire = (
            datetime.utcnow() + expires_delta
            if expires_delta
            else datetime.utcnow() + timedelta(minutes=15)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def get_current_user_name(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username = payload.get("sub")
        except jwt.PyJWTError:
            return None

        return username
