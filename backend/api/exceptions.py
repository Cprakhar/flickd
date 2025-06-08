from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError as FastAPIRequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
import logging

logger = logging.getLogger("flickd.exceptions")

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTPException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail},
    )

async def validation_exception_handler(request: Request, exc: FastAPIRequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "Validation error", "details": exc.errors()},
    )

async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": "Internal server error"},
    )
