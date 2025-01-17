from typing import Annotated, List
from fastapi import APIRouter, Query, Path, status, Body, Depends, Request
from app.db.index import get_session
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from rich import print
from app.auth.dependencies import get_current_user
from app.auth.schemas import UserBase2
from fastapi.responses import HTMLResponse
from .service import get_book_review_service,new_book_review
from .schemas import BaseReview, ReviewSchema


route = APIRouter(tags=["Review"])



@route.post("/add_review/{book_uid}",response_model=ReviewSchema, status_code= status.HTTP_201_CREATED)
async def create_review_for_book(
    book_uid: uuid.UUID, session:
    Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[dict, Depends(get_current_user)],
    review_data: Annotated[BaseReview, Body(embed=True)]):

  new_review = await new_book_review(book_uid, session, review_data, current_user.get("current_user"))
  return new_review




@route.get("/{book_uid}",status_code= status.HTTP_200_OK)
async def get_book_review(
    book_uid: uuid.UUID, session: Annotated[AsyncSession, Depends(get_session)]):
  review = await get_book_review_service(book_uid, session)
  return review




