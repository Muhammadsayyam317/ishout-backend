from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        detail = exc.detail

        payload = {
            "error": {
                "status_code": exc.status_code,
                "message": (
                    detail.get("message") if isinstance(detail, dict) else detail
                ),
                "details": detail.get("details") if isinstance(detail, dict) else None,
            }
        }
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        payload = {
            "error": {
                "status_code": 422,
                "message": "Validation error",
                "details": exc.errors(),
            }
        }
        return JSONResponse(status_code=422, content=payload)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        payload = {
            "error": {
                "status_code": 500,
                "message": "Internal server error",
            }
        }
        return JSONResponse(status_code=500, content=payload)
