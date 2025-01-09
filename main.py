
from fastapi import FastAPI
from app.books.routes import routes as book_routes

version = "0.1.0"
app = FastAPI(
  title="Book API",
  version=version,
  description="A simple REST API for managing books.",
  openapi_url=f"/openapi/{version}"
)


"""
@app.get("/headers/")
async def get_test_header(accept: str = Header(None), content_type: str = Header(None)):
  req_headers = {"Accept": accept, "Content-Type": content_type}
  return req_headers
"""


app.include_router(book_routes, prefix=f"/api/{version}/books",)



if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", port=8000, reload=True)