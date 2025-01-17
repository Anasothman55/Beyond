from fastapi import FastAPI
from fastapi import Request
import time
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
logger = logging.getLogger("uvicorn.access")
logger.disabled = True

def register_middleware(app: FastAPI):


  @app.middleware('http')
  async def custom_logging(request: Request, call_next):
    start_time = time.time()
    print('before', start_time )

    response = await call_next(request)

    processing_time = time.time() - start_time
    message = f"{request.method} - {request.url.path} - completed after {processing_time}s"
    print(message)

    response.headers["X-Custom-Header"] = "Byound"
    return response

  app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )

  app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=['127.0.0.1', 'localhost']
  )





















