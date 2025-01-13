from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, EmailStr,field_validator
import uuid
import enum



class UserBase(BaseModel):
  username: str = Field(max_length= 128)
  email: EmailStr =  Field(max_length= 128)
  first_name: str = Field(None, max_length= 128, pattern=r"^[A-Za-z]+$")
  last_name: str = Field(None,max_length= 128, pattern=r"^[A-Za-z]+$")

  model_config = ConfigDict(
    str_strip_whitespace=True,
    json_schema_extra={
      "example": {
        "username": "john_doe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe"
      }
    }
  )

class UserRegister(UserBase):
  password: str = Field(min_length=8)
  @field_validator('password')
  def validate_password(cls, value, info):
    email = info.data.get("email")
    if email:
      email_local_part = email.partition(email)[0]
      if value in email_local_part:
        raise ValueError("Password cannot contain the email local part.")
    return value

  model_config = ConfigDict(
    str_strip_whitespace=True,
    json_schema_extra={
      "example": {
        "username": "john_doe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "password123"
      }
    }
  )


class UserLogin(BaseModel):
  email: EmailStr
  password: str = Field(min_length=8)

  model_config = ConfigDict(
    str_strip_whitespace=True,
    json_schema_extra={
      "example": {
        "email": "john.doe@example.com",
        "password": "password123"
      }
    }
  )


class GetUser(UserBase):
  uid: uuid.UUID
  updated_at: datetime
  created_at: datetime
  is_verified: bool

  model_config = ConfigDict(
    str_strip_whitespace=True,
    json_schema_extra={
      "example": {
        "username": "john_doe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe"
      }
    }
  )

class TokenBase(BaseModel):
  access_token: str
  token_type: str

class TokenSchema(TokenBase):
  refresh_token: str


class TokenData(BaseModel):
  uid: uuid.UUID | None = None
  refresh: bool = False



