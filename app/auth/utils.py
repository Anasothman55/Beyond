import logging

from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import timezone, timedelta, datetime
from jose import JWTError, jwt,ExpiredSignatureError
from sqlalchemy.orm import joinedload,selectinload
from rich import print
from app.config import settings
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db.models import UserModel
import uuid
from itsdangerous import URLSafeTimedSerializer






pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password_utils(password: str) -> str:
  return pwd_context.hash(password)
def verify_password_utils(password: str, hashed_password: str) -> bool:
  return pwd_context.verify(password, hashed_password)




def create_access_token(data:dict,expires_delta: timedelta | None = None, refresh: bool = False):
  to_encod = data.copy()

  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else:
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)

  to_encod.update({"exp": expire})
  to_encod.update({"refresh": refresh})

  encoded_jwt = jwt.encode(to_encod, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
  return encoded_jwt

def create_refresh_token(data:dict, expires_delta: timedelta | None = None, refresh: bool = True):
  to_encod = data.copy()

  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else:
    expire = datetime.now(timezone.utc) + timedelta(days=7)

  to_encod.update({"exp": expire})
  to_encod.update({"refresh": refresh})
  encoded_jwt = jwt.encode(to_encod, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
  return encoded_jwt


def jwt_decode(token: str, options: dict | None = None):
  try:
    if options:
      payload = jwt.decode(token, settings.SECRET_KEY,algorithms= settings.ALGORITHM, options=options)
    else:
      payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    return payload
  except JWTError as jex:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'error': str(jex), 'message': "Invalid"})



async def get_user_by_uid(uid: uuid.UUID, session: AsyncSession):
  statement = select(UserModel).where(UserModel.uid == uid)
  result = await session.execute(statement)
  user = result.scalar_one_or_none()

  return user


async def get_user_by_email(email:EmailStr, session: AsyncSession):
  statement = select(UserModel).where(UserModel.email == email)
  result = await session.execute(statement)
  return result.scalars().first()

async def authenticate_user(session: AsyncSession, email: EmailStr, password: str):
  user = await get_user_by_email(email, session)

  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
      "message": "Invalid credentials wrong email address",
      "loc": "email",
      "data": email
    })

  if not verify_password_utils(password, user.password_hash):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED, detail={
        "message": "Invalid credentials wrong password",
        "loc": "password",
        "data": password
      }
    )

  return user


def httpresponse(status, details: dict):
  raise HTTPException(status_code= status, detail=details)




serializer = URLSafeTimedSerializer(
  secret_key=settings.SECRET_KEY,
  salt="email-config"
)

def create_url_safe_token(data: dict):
  token = serializer.dumps(data)
  return token

def decode_url_safe_token(token: str):
  try:
    token_data = serializer.loads(token)
    return token_data
  except Exception as e:
    logging.error(str(e))
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"message": "Invalid token"})



