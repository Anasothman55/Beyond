from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from .schemas import BookBase,UpdateBook
from sqlmodel import select, desc, asc
from .models import BookModel
from fastapi import HTTPException, status


async def get_by_uid(uid: uuid.UUID, session: AsyncSession):
  statement = select(BookModel).where(BookModel.uid == uid)
  result = await session.execute(statement)
  return result.scalars().first()


async def get_all_books(session: AsyncSession, order_by: str = 'created_at'):
  order_column = getattr(BookModel, order_by, BookModel.created_at)
  
  if order_by.startswith('-'):
    order_column = desc(order_column)  
  else:
    order_column = asc(order_column)
  
  statement = select(BookModel).order_by(order_column)
  result = await session.execute(statement)
  
  return result.scalars().all()
async def get_a_book( uid:uuid.UUID ,session: AsyncSession):
  book = await get_by_uid(uid, session)
  if not book:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with uid {uid} not found")
  return book.model_dump()
async def create_book( book_data: BookBase, session: AsyncSession):
  new_book = BookModel(**book_data.model_dump())
  
  session.add(new_book)
  await session.commit()
  await session.refresh(new_book)
  
  return new_book.model_dump()
async def update_book( uid:uuid.UUID ,book_data: UpdateBook,session: AsyncSession):
  get_book = await get_by_uid(uid, session)
  update_a_book = book_data.model_dump()
  
  for k, v in update_a_book.items():
    if v:
      setattr(get_book, k, v)
  
  await session.commit()
  await session.refresh(get_book)
  return get_book
async def delete_book(uid:uuid.UUID ,session: AsyncSession):
  get_book = await get_by_uid(uid, session)
  
  await session.delete(get_book)
  await session.commit()





