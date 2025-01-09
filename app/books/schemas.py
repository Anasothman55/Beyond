from datetime import datetime, date
from pydantic import BaseModel, Field
import uuid
import enum


#! Enum

class SortEnum(enum.Enum):
  title = "title"
  author = "author"
  published_date = "published_date"
  page_count = "page_count"
  language = "language"
  created_at = "created_at"
  updated_at = "updated_at"
  
  def to_str(self):
    return self.value

#! schemas
class BookBase(BaseModel):
  title: str
  author: str
  publisher: str
  published_date: date
  page_count: int
  language: str



class ReturnAllBook(BookBase):
  uid: uuid.UUID
  updated_at: datetime
  created_at: datetime

class UpdateBook(BaseModel):
  title: str | None = None
  author: str | None = None
  publisher: str | None = None
  published_date: date | None = None
  page_count: int | None = Field(None, gt=0)
  language: str | None = None
