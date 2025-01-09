from typing import Annotated, List, Sequence
from fastapi import APIRouter, Query, Path, status, HTTPException, Body
from app.books.books import books_data
from app.books.schemas import *


routes = APIRouter(tags=["Books"])

#! endpoint
def get_one_book(bid: int,bdb: list):
  for book in bdb:
    if book.get("id") == bid:
      return  book
  else:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@routes.get("/", response_model= List[BookBase], status_code= status.HTTP_200_OK)
async  def get_all_books(
    start: Annotated[int, Query(ge=0)] =0,
    limit: Annotated[int, Query()] = len(books_data)-1
  ):
  return books_data[start:limit+start]

@routes.post("/", response_model= BookBase, status_code= status.HTTP_201_CREATED)
async def add_book(book_req: Annotated[BookBase, Body(embed=True)]) -> dict:
  book_dict = book_req.model_dump()
  books_data.append(book_dict)
  return book_dict

@routes.get("/{book_id}", response_model= BookBase, status_code= status.HTTP_200_OK)
async  def get_a_book(book_id: Annotated[int, Path(gt=0)]) -> dict:
  book = get_one_book(book_id, books_data)
  return book

@routes.patch("/{book_id}", response_model= BookBase, status_code= status.HTTP_202_ACCEPTED)
async  def patch_a_book(book_id: Annotated[int, Path(gt=0)], req_data: Annotated[UpdateBook, Body()]) -> dict:
  book = get_one_book(book_id, books_data)
  req_data_dict = req_data.model_dump()
  for k, v in dict(book).items():
    if k in req_data_dict and req_data_dict.get(k) != None:
      book[k] = req_data_dict[k]
  return book


@routes.delete("/{book_id}", status_code= status.HTTP_204_NO_CONTENT)
async  def delete_a_book(book_id: Annotated[int, Path(gt=0)]):
  book = get_one_book(book_id, books_data)
  books_data.remove(book)
