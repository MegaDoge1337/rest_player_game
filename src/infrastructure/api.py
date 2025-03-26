import os
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from domain.services import GameService

from .auth import Auth
from .dto import User, Event, Action, ActionResult, Token

from .database import SessionFactory

from .repositories import (
    SqlAlchemyUserRepository,
    SqlAlchemyInventoryRepository,
    SqlAlchemyScoreRepository,
    SqlAlchemyEventRepository,
    OpenAILLMRepository,
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()

session = SessionFactory()

user_repo = SqlAlchemyUserRepository(session=session)
inventroy_repo = SqlAlchemyInventoryRepository(session=session)
score_repo = SqlAlchemyScoreRepository(session=session)
event_repo = SqlAlchemyEventRepository(session=session)
llm_repo = OpenAILLMRepository()

service = GameService(
    user_repo=user_repo,
    inventory_repo=inventroy_repo,
    score_repo=score_repo,
    event_repo=event_repo,
    llm_repo=llm_repo,
)

auth = Auth(game_service=service)


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
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
    return Token(access_token=access_token, token_type="bearer")


@app.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    hashed_password = auth.get_password_hash(form_data.password)
    try:
        user = service.create_user(form_data.username, hashed_password)
        return User(
            name=user.name, inventory=user.inventory.items, score=user.score.score
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"User with name {form_data.username} already exists",
        )


@app.get("/user")
async def get_current_user(current_user=Depends(auth.get_current_user)):
    return User(
        name=current_user.name,
        inventory=current_user.inventory.items,
        score=current_user.score.score,
    )


@app.post("/act")
async def make_action(action: Action, current_user=Depends(auth.get_current_user)):
    result = service.make_action(current_user, action.action)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to make action: Internal server error",
        )

    service.write_event(current_user, result.description)
    return ActionResult(
        description=result.description, inventory=result.inventory, score=result.score
    )


@app.get("/user/events/{page}")
async def get_user_events(page: int, current_user=Depends(auth.get_current_user)):
    events = service.get_user_events(current_user, page)
    return [
        Event(
            description=event.description,
            user=User(
                name=event.user.name,
                inventory=event.user.inventory.items,
                score=event.user.score.score,
            ),
        )
        for event in events
    ]


@app.get("/events/{page}")
async def get_all_events(page: int, _=Depends(auth.get_current_user)):
    events = service.get_all_events(page)
    return [
        Event(
            description=event.description,
            user=User(
                name=event.user.name,
                inventory=event.user.inventory.items,
                score=event.user.score.score,
            ),
        )
        for event in events
    ]
