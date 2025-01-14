from typing import Annotated, List
from fastapi import APIRouter, Query, Path, status, Body, Depends, Request
from app.books.schemas import BookBase,ReturnAllBook,UpdateBook, SortEnum
from app.db.index import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .service import get_all_books as gab, create_book, get_a_book, update_book, delete_book
import uuid
from rich import  print


routes = APIRouter(tags=["Books"])

@routes.get("/req_check")
async def get_req_check(req: Request):
  print(req.__dict__.get('_send'))
  return "anas"

@routes.get("/", response_model= List[ReturnAllBook], status_code= status.HTTP_200_OK)
async  def get_all_books(
    *,
    session:Annotated[AsyncSession, Depends(get_session)],
    order_by: Annotated[SortEnum, Query()] = "created_at",
    descending: Annotated[bool, Query()] = False,
  ):
  order_by = str(order_by).lower()
  if descending:
    order_by = f"-{order_by}"
  service_data = await gab(session, order_by)
  return service_data

@routes.post("/", response_model= BookBase, status_code= status.HTTP_201_CREATED)
async def add_book(
    book_req: Annotated[BookBase, Body(embed=True)],
    session:Annotated[AsyncSession, Depends(get_session)]
  ) -> dict:
  service_data = await create_book(book_req, session)
  return service_data

@routes.get("/{book_id}", response_model= ReturnAllBook,response_model_exclude={"uid"}, status_code= status.HTTP_200_OK)
async  def get_one_book(book_id: Annotated[uuid.UUID, Path()], session:Annotated[AsyncSession, Depends(get_session)]) -> dict:
  book = await get_a_book(book_id, session)
  
  return book

@routes.patch("/{book_id}", response_model= ReturnAllBook, status_code= status.HTTP_202_ACCEPTED)
async  def patch_a_book(
  book_id: Annotated[uuid.UUID, Path()],
  req_data: Annotated[UpdateBook, Body()],
  session:Annotated[AsyncSession, Depends(get_session)]
  ) -> dict:
  book = await update_book(book_id, req_data,session)
  return book


@routes.delete("/{book_id}", status_code= status.HTTP_204_NO_CONTENT)
async  def delete_a_book(
  book_id: Annotated[uuid.UUID, Path()],
  session:Annotated[AsyncSession, Depends(get_session)]
  ):
  await delete_book(book_id, session)


