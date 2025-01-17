from sqlmodel import select
import uuid
from app.db.index import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Review
from .schemas import ReviewSchema,BaseReview
from app.books.service import get_a_book
from app.db.models import UserModel



async def get_book_review_service(book_uid: uuid.UUID, session: AsyncSession):
  review_query = select(Review).where(Review.book_uid == book_uid)
  reviews = await session.execute(review_query)

  return reviews.scalars().fetchall()


async def new_book_review(
    book_uid: uuid.UUID,
    session: AsyncSession,
    review_data: BaseReview, user: UserModel
  ):
  book = await get_a_book(book_uid, session)
  new_review =  Review(**review_data.model_dump())
  new_review.book = book
  new_review.user = user

  session.add(new_review)
  await session.commit()
  await session.refresh(new_review)

  return new_review










