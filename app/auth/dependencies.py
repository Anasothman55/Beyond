from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from .utils import jwt_decode, get_user_by_uid
import uuid
from app.db.index import get_session
from .schemas import TokenData
from jose.exceptions import JWTError, ExpiredSignatureError
from app.db.redis import token_manager


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

    jit = payload.get("jit")
    if not jit:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid JIT token"
      )

    await token_manager.is_jit_blacklisted(jit)

    token_data = TokenData(uid=uid)
    user = await get_user_by_uid(token_data.uid, session)

    if user is None:
      raise credentials_exception

    return {"current_user":user, "token":token}

  except ExpiredSignatureError:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Token has expired"
    )
  except JWTError:
    raise credentials_exception





