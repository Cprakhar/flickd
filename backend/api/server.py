from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .recommendations import router as recommendations_router
from .videos import router as videos_router
from config import VIDEOS_DIR
from .exceptions import http_exception_handler, validation_exception_handler, generic_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace with your deployed frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(recommendations_router)
app.include_router(videos_router)

app.mount("/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
