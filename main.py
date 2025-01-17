from sqlalchemy import text
from fastapi import FastAPI, status, HTTPException, Depends, Response
from sqlalchemy.testing.config import any_async
from middleware import register_middleware
from app.books.routes import routes as book_routes, global_book as global_book_routes
from app.auth.routes import routes as auth_routes
from app.review.route import route as review_routes
from contextlib import asynccontextmanager
from app.db.index import get_session,AsyncSession,close_db_connection,init_db
from fastapi.responses import JSONResponse, RedirectResponse
from app.db.redis import token_manager
import logging




@asynccontextmanager
async def life_span(app:FastAPI):
  # Startup
  try:
    await init_db()
    print("Application startup complete")
  except Exception as e:
    print(f"Error during startup: {e}")
    raise
  yield
  # Shutdown
  try:
    await close_db_connection()
    print("Database connection closed")
  except Exception as e:
    print(f"Error closing database connection: {e}")


logging.basicConfig(
    level=logging.INFO,  # Set logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log message format
)


version = "0.1.0"
app = FastAPI(
  title="Book API",
  version=version,
  description="A simple REST API for managing books.",
  lifespan=life_span
)

#http://127.0.0.1:8000/openapi.json
logger = logging.getLogger(__name__)

"""
@app.get("/headers/")
async def get_test_header(accept: str = Header(None), content_type: str = Header(None)):
  req_headers = {"Accept": accept, "Content-Type": content_type}
  return req_headers
"""

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check_postgresql(session: AsyncSession = Depends(get_session)):
  try:
    # Test database connection
    result = await session.execute(text("SELECT 1"))
    await session.commit()
    redis_helth = await token_manager.redis.set('foo', 'anas othman')
    
    if not redis_helth:
      raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis connection failed")
    
    return {
      "status": "healthy",
      "database": "connected",
      "message": "Application is running normally",
      "execute": result
    }
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      detail=f"Database connection failed: {str(e)}"
    )

"""
@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})
"""

@app.exception_handler(500)
async def internal_server_error(request, ext):
  return JSONResponse(
    status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={"detail": "Internal Server Error", "error": str(ext)}
  )

register_middleware(app)


app.include_router(auth_routes, prefix=f"/api/{version}/auth",)
app.include_router(global_book_routes, prefix=f"/api/{version}/global_books",)
app.include_router(book_routes, prefix=f"/api/{version}/books",)
app.include_router(review_routes, prefix=f"/api/{version}/reviews")

"""
alembic
1- alembic init -t async migrations
2-  alembic revision --autogenerate -m "add review table"
3- alembic upgrade 4fa398e4f096    
"""
  



if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", port=8000, reload=True)