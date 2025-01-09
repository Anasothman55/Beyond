from datetime import datetime, date
from pydantic import BaseModel, Field


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
