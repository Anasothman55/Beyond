from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from watchfiles import awatch
from .schemas import UserRegister, UserBase, UserLogin, GetUser
from sqlmodel import select, desc, asc
from sqlalchemy.exc import IntegrityError
from .models import UserModel
from fastapi import HTTPException, status
from app.auth import hash_password_utils, verify_password_utils
from .utils import get_user_by_uid,authenticate_user, create_access_token,create_refresh_token, jwt_decode, JWTError, ExpiredSignatureError
from ..config import settings
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from app.db.redis import is_token_blacklisted, get_refresh_token, store_refresh_token,blacklist_access_token, blacklist_refresh_token, delete_refresh_token, is_token_jit_blacklisted



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

  #!if not user.is_verified:
  #!  raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not verified")
  
  jit =  str(uuid.uuid4())
  access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = create_access_token (
    data={"sub": str(user.uid), "username":user.username, "jit": jit}, expires_delta=access_token_expire
  )
  refresh_token_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
  refresh_token = create_refresh_token(
    data={"sub": str(user.uid),"ati": jit}, expires_delta=refresh_token_expire
  )
  
  setRedis = await store_refresh_token(user_id=user.uid, refresh_token= refresh_token,ttl_days= settings.REFRESH_TOKEN_EXPIRE_DAYS)
  if not setRedis:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="No valid session found"
    )
    
  return {"access_token": access_token,"refresh_token":refresh_token, "token_type": "bearer"}



async def refresh_token_service(current_token: str):
  try:
    # Get user ID from expired access token
    payload = jwt_decode(current_token, options={"verify_exp": False})
    user_id = payload.get("sub")
    jit = payload.get("jit")

    is_in_jit_black_list = await is_token_jit_blacklisted(jit)

    if is_in_jit_black_list:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="JIT token has been blacklisted"
      )

    stored_refresh_token = await get_refresh_token(user_id=user_id)
    if not stored_refresh_token:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No valid session found"
      )
    
    is_in_black_list = await is_token_blacklisted(stored_refresh_token)
    if is_in_black_list:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token has been blacklisted"
      )

    # Verify the refresh token
    refresh_payload = jwt_decode(stored_refresh_token)
    refresh_user_id = refresh_payload.get("sub")
    if user_id!= refresh_user_id:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token"
      )

    jit_blacklist = await blacklist_access_token(jit)
    print(jit_blacklist)
    if not jit_blacklist:
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to blacklist access token"
      )

    # Create new access token
    jit = str(uuid.uuid4())
    access_token = create_access_token(
      data={
        "sub": user_id,
        "username": refresh_payload.get("username"),
        "jit": jit
      },
      expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
      "access_token": access_token,
      "token_type": "bearer"
    }

  except ExpiredSignatureError:
      # Handle expired JWT token
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token expired")
  except JWTError as e:
      # Log the exception and return a more specific error message
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")


async def logout_service(token: dict):
  try:
    # Decode the token
    token_decode = token
    user_uid = token_decode.get("sub")
    jit = token_decode.get("jit")

    if not user_uid or not jit:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token"
      )

    # Blacklist the JIT (JWT ID) for the access token
    jit_blacklist = await blacklist_access_token(jit)
    print(jit_blacklist)
    if not jit_blacklist:
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to blacklist access token"
      )

    # Retrieve and validate the refresh token
    stored_refresh_token = await get_refresh_token(user_id=user_uid)
    if not stored_refresh_token:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No valid session found"
      )

    # Check if the refresh token is already blacklisted
    if await is_token_blacklisted(stored_refresh_token):
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token has been blacklisted"
      )

    # Verify the refresh token belongs to the user
    refresh_payload = jwt_decode(stored_refresh_token)
    if refresh_payload.get("sub") != user_uid:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token"
      )


    # Blacklist the refresh token
    refresh_token_add_blacklist = await blacklist_refresh_token(stored_refresh_token)
    if not refresh_token_add_blacklist:
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to blacklist refresh token"
      )

    delete_result = await delete_refresh_token(user_uid,stored_refresh_token)
    if not delete_result:
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to delete refresh token from Redis"
      )

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
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"An error occurred: {str(e)}"
    )







