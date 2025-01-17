# services


from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from .schemas import UserRegister
from sqlalchemy.exc import IntegrityError
from app.db.models import UserModel
from fastapi import HTTPException, status
from .utils import hash_password_utils, verify_password_utils
from .utils import get_user_by_uid,authenticate_user, create_access_token,create_refresh_token, jwt_decode, JWTError, ExpiredSignatureError, httpresponse
from ..config import settings
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from app.db.redis import RedisManager
from app.autils import http_exception



redis_config = {
  'host': settings.UPSTASH_REDIS_HOST,
  'port': settings.UPSTASH_REDIS_PORT,
  'password': settings.UPSTASH_REDIS_PASSWORD,
  'ssl': settings.UPSTASH_REDIS_SSL
}

# Initialize token manager
token_manager = RedisManager(redis_config)

async def make_token(user_uid,username):
  jit = str(uuid.uuid4())
  fid = str(uuid.uuid4())
  access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = create_access_token(
    data={"sub": str(user_uid), "username": username, "jit": jit, "fid": fid},
    expires_delta=access_token_expire
  )
  refresh_token_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
  refresh_token = create_refresh_token(
    data={"sub": str(user_uid), "fti": str(uuid.uuid4()), "fid": fid}, expires_delta=refresh_token_expire
  )
  await token_manager.store_refresh_token(user_id=user_uid, refresh_token=refresh_token,ttl_days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

  return {
    "access_token": access_token,
    "token_type": "bearer"
  }



async def register_service(
    register_model: UserRegister,
    session: AsyncSession
  ) -> dict:
  try:
    hash_password = register_model.model_dump()
    hash_password["password_hash"] = hash_password_utils(hash_password.get('password'))
    del hash_password['password']

    new_user = UserModel(**hash_password)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)


    return new_user.model_dump()
  except IntegrityError as iex:
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT, detail={
        "message": f"IntegrityError while registering",
        "error": str(iex)
      }
    )


async def user_login_service(form_data: OAuth2PasswordRequestForm, session: AsyncSession):
  user = await authenticate_user(session, form_data.username, form_data.password)

  if not user.is_verified:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not verified")
  
  maketoken = await make_token(user.uid, user.username)
  return maketoken




async def refresh_token_service(current_token: str):
  try:
    payload = jwt_decode(current_token, options={"verify_exp": False})
    user_uid = payload.get("sub")

    srt = await token_manager.get_refresh_token(user_uid)
    refresh_payload = jwt_decode(srt)
    await token_manager.is_token_blacklisted(refresh_payload.get("fti"))

    if user_uid != refresh_payload.get("sub"):
      raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if payload.get('fid') != refresh_payload.get('fid'):
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Un match refresh token and access token"
      )

    maketoken = await make_token(user_uid, payload.get('username'))
    return maketoken

  except ExpiredSignatureError:
      # Handle expired JWT token
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token expired")
  except JWTError as e:
      # Log the exception and return a more specific error message
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")


async def logout_service(token_to_decode):
  try:
    token = jwt_decode(token_to_decode)
    user_uid = str(token.get("sub"))
    srt = await token_manager.get_refresh_token(user_uid)
    refresh_payload = jwt_decode(srt)

    if refresh_payload.get("sub") != user_uid:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token"
      )

    await token_manager.blacklist_refresh_token(refresh_payload.get('fti'))
    await token_manager.blacklist_access_token(token.get('jit'))
    await token_manager.delete_refresh_token(user_uid)

    return {"message": "Logout successful"}
  except ExpiredSignatureError:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Token has expired"
    )
  except JWTError as e:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail=f"Invalid token: {str(e)}"
    )








