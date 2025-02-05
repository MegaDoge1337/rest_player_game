import os
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .auth import Auth
from .dto import Token

from .database import SessionFactory

from .repositories import SqlAlchemyUserRepository

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1"))

app = FastAPI()


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    session = SessionFactory()
    user_repo = SqlAlchemyUserRepository(session=session)
    auth = Auth(user_repo=user_repo)

    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user name or password",
            headers={"WWW-Authentificate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    session = SessionFactory()
    user_repo = SqlAlchemyUserRepository(session=session)
    auth = Auth(user_repo=user_repo)

    user = user_repo.get_user_by_name(form_data.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"User with name {form_data.username} already exists"
        )
    
    hashed_password = auth.get_password_hash(form_data.password)
    return user_repo.create_user(form_data.username, form_data.password)
