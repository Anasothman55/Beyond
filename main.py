from sqlalchemy import text
from fastapi import FastAPI, status, HTTPException, Depends
from app.books.routes import routes as book_routes
from contextlib import asynccontextmanager
from app.db.index import get_session,AsyncSession,close_db_connection,init_db


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


version = "0.1.0"
app = FastAPI(
  title="Book API",
  version=version,
  description="A simple REST API for managing books.",
  openapi_url=f"/openapi/{version}",
  lifespan=life_span
)


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



app.include_router(book_routes, prefix=f"/api/{version}/books",)



if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", port=8000, reload=True)