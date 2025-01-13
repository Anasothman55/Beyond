from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from .utils import jwt_decode, get_user_by_uid
from app.db.redis import is_token_jit_blacklisted
import uuid
from app.db.index import get_session
from .schemas import TokenData
from jose.exceptions import JWTError, ExpiredSignatureError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="access_token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt_decode(token)

    # Check if token is a refresh token
    if  payload.get("refresh", False):
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Cannot use refresh token for authentication"
      )

    uid = uuid.UUID(payload.get("sub"))
    if uid is None:
      raise credentials_exception

    is_in_jit_black_list = await is_token_jit_blacklisted(payload.get("jit"))

    if is_in_jit_black_list:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="JIT token has been blacklisted"
      )

    token_data = TokenData(uid=uid)
    user = await get_user_by_uid(token_data.uid, session)

    if user is None:
      raise credentials_exception

    return {"current_user":user, "token":payload}

  except ExpiredSignatureError:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Token has expired"
    )
  except JWTError:
    raise credentials_exception





