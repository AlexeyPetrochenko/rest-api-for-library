import logging

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.web.exceptions import AppBaseError

logger = logging.getLogger(__name__)

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


async def handler_base_app_exc(request: Request, exc: AppBaseError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "status": HTTP_ERROR_CODES[exc.status_code],
            "detail": jsonable_encoder(exc.detail),
            "error_name": exc.__class__.__name__,
            "from_error": jsonable_encoder(exc.__cause__),
        }
    )
