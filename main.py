from typing import Annotated, List
from pydantic import BaseModel, Field
from fastapi import FastAPI, Query, Header, Path, status, HTTPException, Body, Request
from books import books_data
from datetime import datetime, date

app = FastAPI()


"""
@app.get("/headers/")
async def get_test_header(accept: str = Header(None), content_type: str = Header(None)):
  req_headers = {"Accept": accept, "Content-Type": content_type}
  return req_headers
"""


#! schemas
class BookBase(BaseModel):
  id: int
  title: str
  author: str
  publisher: str
  published_date: date
  page_count: int
  language: str
class UpdateBook(BaseModel):
  title: str | None = None
  author: str | None = None
  publisher: str | None = None
  published_date: date | None = None
  page_count: int | None = Field(None, gt=0)
  language: str | None = None


#! endpoint
def get_one_book(bid: int,bdb: list):
  for book in bdb:
    if book.get("id") == bid:
      return  book
  else:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@app.get("/books", response_model= List[BookBase], status_code= status.HTTP_200_OK)
async  def get_all_books(
    start: Annotated[int, Query(ge=0)] =0,
    limit: Annotated[int, Query()] = len(books_data)-1
  ):
  return books_data[start:limit+start]

@app.post("/books", response_model= BookBase, status_code= status.HTTP_201_CREATED)
async def add_book(book_req: Annotated[BookBase, Body(embed=True)]) -> dict:
  book_dict = book_req.model_dump()
  books_data.append(book_dict)
  return book_dict

@app.get("/books/{book_id}", response_model= BookBase, status_code= status.HTTP_200_OK)
async  def get_a_book(book_id: Annotated[int, Path(gt=0)]) -> dict:
  book = get_one_book(book_id, books_data)
  return book

@app.patch("/books/{book_id}", response_model= BookBase, status_code= status.HTTP_202_ACCEPTED)
async  def patch_a_book(book_id: Annotated[int, Path(gt=0)], req_data: Annotated[UpdateBook, Body()]) -> dict:
  book = get_one_book(book_id, books_data)
  req_data_dict = req_data.model_dump()
  for k, v in dict(book).items():
    if k in req_data_dict and req_data_dict.get(k) != None:
      book[k] = req_data_dict[k]
  return book


@app.delete("/books/{book_id}", status_code= status.HTTP_204_NO_CONTENT)
async  def delete_a_book(book_id: Annotated[int, Path(gt=0)]):
  book = get_one_book(book_id, books_data)
  books_data.remove(book)



if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", port=8000, reload=True)