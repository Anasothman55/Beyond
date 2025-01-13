from fastapi import APIRouter, Query, Path, status, Body, Depends
from app.auth.schemas import UserBase, UserRegister, GetUser, TokenSchema, TokenBase
from app.db.index import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .service import register_service, user_login_service, refresh_token_service,logout_service
from fastapi.security import OAuth2PasswordRequestForm
from .dependencies import get_current_user, oauth2_scheme



routes = APIRouter(tags=["Auth"])


@routes.post("/register", response_model=UserBase, status_code= status.HTTP_201_CREATED)
async def register_routes(
    register_model: Annotated[UserRegister, Body(embed=True)],
    session: Annotated[AsyncSession, Depends(get_session)]
  ):

  response_date = await register_service(register_model, session)
  return response_date


@routes.post("/get_token", response_model=TokenSchema, status_code=status.HTTP_202_ACCEPTED)
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)]
  ):
  token_data = await user_login_service(form_data, session)
  return token_data

@routes.post("/logout", status_code= status.HTTP_200_OK)
async def logout(current_user: Annotated[GetUser, Depends(get_current_user)]):
  current_token = current_user.get("token")
  result = await logout_service(current_token)
  return result

@routes.post("/refresh", response_model=TokenBase)
async def refresh_access_token(
    *,
    access_token= Depends(oauth2_scheme),
):
  response_model = await refresh_token_service(access_token)
  return response_model


@routes.get("/get_me", response_model=GetUser, response_model_exclude={'created_at','updated_at'}, status_code= status.HTTP_200_OK)
async def read_users_me( current_user: Annotated[GetUser, Depends(get_current_user)]):
  #? new_lamb= dict(map(lambda item: (item[0], str(item[1])), current_user.model_dump().items()))
  #? return JSONResponse(new_lamb)
  user_data = current_user.get("current_user")
  return user_data













