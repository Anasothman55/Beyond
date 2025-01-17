
from fastapi import APIRouter, status, Body, Depends, HTTPException, BackgroundTasks

from app.auth.schemas import UserBase, UserRegister, GetUser, TokenBase,EmailBaseModel
from app.db.index import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .service import register_service, user_login_service, refresh_token_service,logout_service
from fastapi.security import OAuth2PasswordRequestForm
from .dependencies import get_current_user, oauth2_scheme
from app.email import create_message,mail
from app.config import settings
from .utils import create_url_safe_token, decode_url_safe_token, get_user_by_email
from fastapi.responses import HTMLResponse





routes = APIRouter(tags=["Auth"])




@routes.post('/send_email')
async def send_email(emails: EmailBaseModel):
  email = emails.address

  html =  """
  <html>
    <body>
      <h1>Welcome to our website!</h1>
      <p>Click the link below to verify your email address:</p>
      <a href="{verify_url}">Verify email</a>
    </body>
  </html>
  """

  #message = create_message(recipients=email, subject="Welcome To our platform", body=html)
  #await mail.send_message(message)


  return {"message": "Email send successfully"}




@routes.post("/register", response_model=UserBase, status_code= status.HTTP_201_CREATED)
async def register_routes(
    bg_tasks: BackgroundTasks,
    register_model: Annotated[UserRegister, Body(embed=True)],
    session: Annotated[AsyncSession, Depends(get_session)]
  ):  
  response_date = await register_service(register_model, session)

  token= create_url_safe_token({"email": register_model.email})

  link = f"http://{settings.DOMAIN}/api/0.1.0/auth/verify-email/{token}"
  register_html_message = f"""
  <html>
    <body>
      <h1>Welcome to our website!</h1>
      <p>Your username is: {register_model.username}</p>
      <p>Please confirm your email address by clicking the link below:</p>
      <a href={link}/>Verify email</a>
    </body>
  </html>
  """

  #message = create_message(recipients=[register_model.email], subject="Welcome To our platform", body=register_html_message)
  #await mail.send_message(message)

  return response_date


@routes.post("/get_token", response_model=TokenBase, status_code=status.HTTP_202_ACCEPTED)
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)]
  ):
  token_data = await user_login_service(form_data, session)
  return token_data


@routes.get("/verify-email/{token}")
async def verify_email(token: str, session: Annotated[AsyncSession, Depends(get_session)]):

  token_data = decode_url_safe_token(token)
  user_email = token_data.get("email", None)


  if user_email:
    user = await get_user_by_email(user_email, session)
    if not user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_verified = True
    await session.commit()
    await session.refresh(user)
  else:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

  return HTMLResponse("""
  <html>
  <body>
  <h1>Email Verification</h1>
  <p>Your email has been verified. You can now log in to your account.</p>
  </body>
  </html>
  """)

@routes.post("/logout", status_code= status.HTTP_200_OK)
async def logout(current_user: Annotated[dict, Depends(get_current_user)]):
  current_token = current_user.get("token")
  result = await logout_service(current_token)
  return result


@routes.post("/refresh", response_model=TokenBase)
async def refresh_access_token(access_token= Depends(oauth2_scheme),):
  response_model = await refresh_token_service(access_token)
  return response_model


@routes.get("/get_me", response_model=GetUser, response_model_exclude={'created_at','updated_at'}, status_code= status.HTTP_200_OK)
async def read_users_me( current_user: Annotated[dict, Depends(get_current_user)]):
  #? new_lamb= dict(map(lambda item: (item[0], str(item[1])), current_user.model_dump().items()))
  #? return JSONResponse(new_lamb)

  user_data = current_user.get("current_user")
  return user_data













