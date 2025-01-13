
from sqlmodel import SQLModel,Field,Column
from datetime import datetime,timezone
import sqlalchemy.dialects.postgresql as pg
import uuid




class UserModel(SQLModel, table=True, ):
  uid: uuid.UUID = Field(
    sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4)
  )
  username: str = Field(unique=True, index=True)
  email: str = Field(unique=True, index=True)
  first_name: str = Field(index=True)
  last_name: str = Field(index=True)
  is_verified: bool = Field(default = False)
  password_hash: str = Field(exclude=True)
  created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default= datetime.now(timezone.utc)))
  updated_at: datetime = Field(
    sa_column=Column(pg.TIMESTAMP(timezone=True), default= datetime.now(timezone.utc), onupdate= datetime.now(timezone.utc))
  )

  def __repr__(self):
    return f"<Book {self.username}>"







