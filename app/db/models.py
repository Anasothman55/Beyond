
from sqlmodel import SQLModel,Field,Column, Relationship
from datetime import datetime, date,timezone
import sqlalchemy.dialects.postgresql as pg
import uuid
from typing import Optional, List
from sqlalchemy import Column as sa_Column

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
  user_uid: uuid.UUID | None = Field(default=None, foreign_key="usermodel.uid")
  created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default= datetime.now(timezone.utc)))
  updated_at: datetime = Field(
    sa_column=Column(pg.TIMESTAMP(timezone=True), default= datetime.now(timezone.utc), onupdate= datetime.now(timezone.utc))
  )
  user: Optional["UserModel"] = Relationship(back_populates= "book")
  review: List["Review"] | None = Relationship(back_populates="book", sa_relationship_kwargs={"lazy": "selectin"})

  def __repr__(self):
    return f"<Book {self.title}>"


class UserModel(SQLModel, table=True, ):
  uid: uuid.UUID = Field(
    sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4)
  )
  username: str = Field(unique=True, index=True)
  email: str = Field(unique=True, index=True)
  first_name: str = Field(index=True)
  last_name: str = Field(index=True)
  role: str = Field(sa_column=Column(pg.VARCHAR, server_default="user", index=True ))
  is_verified: bool = Field(default = False)
  password_hash: str = Field(exclude=True)
  created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default= datetime.now(timezone.utc)))
  updated_at: datetime = Field(
    sa_column=Column(pg.TIMESTAMP(timezone=True), default= datetime.now(timezone.utc), onupdate= datetime.now(timezone.utc))
  )

  book: List[BookModel] | None = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
  review: List["Review"] | None = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

  def __repr__(self):
    return f"<Book {self.username}>"



class Review(SQLModel, table=True, ):

  __tablename__ = "reviews"

  uid: uuid.UUID = Field(
    sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4)
  )

  rating: float = Field(gt=0, le=5.0, index=True)
  description: str = Field( sa_column=Column(pg.TEXT) )

  user_uid: uuid.UUID | None = Field(default=None, foreign_key="usermodel.uid")
  book_uid: uuid.UUID | None = Field(default=None, foreign_key="bookmodel.uid")

  created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default= datetime.now(timezone.utc)))
  updated_at: datetime = Field(
    sa_column=Column(pg.TIMESTAMP(timezone=True), default= datetime.now(timezone.utc), onupdate= datetime.now(timezone.utc))
  )

  user: Optional[UserModel] = Relationship(back_populates= "review")
  book: Optional[BookModel] = Relationship(back_populates= "review")

  def __repr__(self):
    return f"<Review for {self.book_uid} by user {self.user_uid}>"









