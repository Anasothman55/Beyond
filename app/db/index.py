from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from ..config import settings
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator


engine = create_async_engine(
  url= settings.POSTGRESQL_URI,
  echo = False,  # Set to False in production
  future = True,
  pool_size = 5,
  max_overflow = 10,
  pool_timeout = 30,
  pool_recycle = 1800,
)

async_session_maker = sessionmaker(
  engine,
  class_=AsyncSession,
  expire_on_commit=False,
)



async def get_session() -> AsyncGenerator[AsyncSession, None]:
  async with async_session_maker() as session:
    try:
      yield session
    except Exception as e:  
      await session.rollback()
      raise
    finally:
      await session.close()

async def close_db_connection():
  await engine.dispose()

async def init_db():
  async with engine.begin() as conn:
    await conn.run_sync(SQLModel.metadata.create_all)