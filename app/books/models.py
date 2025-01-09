
from sqlmodel import SQLModel,Field,Column
from datetime import datetime, date,timezone
import sqlalchemy.dialects.postgresql as pg
import uuid




class BookModel(SQLModel, table=True, ):

  uid: uuid.UUID = Field(
    sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4)
  )
  title: str
  author: str
  publisher: str
  published_date: date
  page_count: int
  language: str
  created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default= datetime.now(timezone.utc)))
  updated_at: datetime = Field(
    sa_column=Column(pg.TIMESTAMP(timezone=True), default= datetime.now(timezone.utc), onupdate= datetime.now(timezone.utc))
  )

  def __repr__(self):
    return f"<Book {self.title}>"



