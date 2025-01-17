from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, EmailStr,field_validator
import uuid
import enum
from typing import  List, Optional


class BaseReview(BaseModel):
  rating: float =  Field(gt=0, le=5.0)
  description: str = Field(max_length=500)

  model_config = ConfigDict(
    str_strip_whitespace= True,
    json_schema_extra={
      "example": {
        "rating": 4.5,
        "description": "This book is great!"
      }
    }
  )



class ReviewSchema(BaseReview):
  uid: uuid.UUID
  user_uid: uuid.UUID






