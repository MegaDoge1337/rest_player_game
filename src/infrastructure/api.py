from fastapi import Depends, FastAPI, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from domain.services import GameService

from .auth import JwtAuth
from .database import SessionFactory
from .repositories import (
    OpenAILLMRepository,
    SqlAlchemyEventRepository,
    SqlAlchemyInventoryRepository,
    SqlAlchemyScoreRepository,
    SqlAlchemyUserRepository,
)


class Action(BaseModel):
    action: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

session = SessionFactory()

auth = JwtAuth()
user_repo = SqlAlchemyUserRepository(session=session)
inventroy_repo = SqlAlchemyInventoryRepository(session=session)
score_repo = SqlAlchemyScoreRepository(session=session)
event_repo = SqlAlchemyEventRepository(session=session)
llm_repo = OpenAILLMRepository()

service = GameService(
    auth=auth,
    user_repo=user_repo,
    inventory_repo=inventroy_repo,
    score_repo=score_repo,
    event_repo=event_repo,
    llm_repo=llm_repo,
)


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        return service.get_access_token(form_data.username, form_data.password)
    except PermissionError as ex:
        return JSONResponse(
            content={"details": str(ex)}, status_code=status.HTTP_401_UNAUTHORIZED
        )


@app.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        return service.create_user(form_data.username, form_data.password)
    except ValueError as ex:
        return JSONResponse(
            content={"details": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST
        )


@app.get("/user")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        return service.get_current_user(token)
    except PermissionError as ex:
        return JSONResponse(
            content={"details": str(ex)}, status_code=status.HTTP_401_UNAUTHORIZED
        )


@app.post("/act")
async def make_action(action: Action, token: str = Depends(oauth2_scheme)):
    try:
        return service.make_action(action.action, token)
    except ConnectionError as ex:
        return JSONResponse(
            content={"details": str(ex)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except ValueError as ex:
        return JSONResponse(
            content={"details": str(ex)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except PermissionError as ex:
        return JSONResponse(
            content={"details": str(ex)}, status_code=status.HTTP_401_UNAUTHORIZED
        )


@app.get("/user/events/{page}")
async def get_user_events(page: int, token: str = Depends(oauth2_scheme)):
    try:
        return service.get_user_events(page, token)
    except PermissionError as ex:
        return JSONResponse(
            content={"details": str(ex)}, status_code=status.HTTP_401_UNAUTHORIZED
        )


@app.get("/events/{page}")
async def get_all_events(page: int, token: str = Depends(oauth2_scheme)):
    try:
        return service.get_all_events(page, token)
    except PermissionError as ex:
        return JSONResponse(
            content={"details": str(ex)}, status_code=status.HTTP_401_UNAUTHORIZED
        )


@app.get("/rating")
async def get_users_with_best_score(token: str = Depends(oauth2_scheme)):
    try:
        return service.get_users_with_best_score(token)
    except PermissionError as ex:
        return JSONResponse(
            content={"details": str(ex)}, status_code=status.HTTP_401_UNAUTHORIZED
        )
