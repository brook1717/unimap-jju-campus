"""
unimap_backend/exceptions.py
-----------------------------
Custom DRF exception handler + a reusable error_response() helper so
every error the API returns (raised exception OR explicit Response) has
the same JSON shape:

    { "error": "ErrorType", "message": "Human-readable detail", "status_code": N }
"""

import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

# Map HTTP status codes → short symbolic names used in the "error" field.
_STATUS_TYPES: dict[int, str] = {
    400: 'BadRequest',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'NotFound',
    405: 'MethodNotAllowed',
    409: 'Conflict',
    422: 'UnprocessableEntity',
    429: 'TooManyRequests',
    500: 'InternalServerError',
}


def error_response(message: str, status_code: int, error_type: str | None = None) -> Response:
    """
    Build a consistently-formatted error Response.

    Usage in views:
        return error_response('Location not found.', 404)
        return error_response('Invalid coordinate.', 400, 'ValidationError')
    """
    return Response(
        {
            'error':       error_type or _STATUS_TYPES.get(status_code, 'Error'),
            'message':     message,
            'status_code': status_code,
        },
        status=status_code,
    )


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    """
    DRF exception handler registered via REST_FRAMEWORK['EXCEPTION_HANDLER'].

    Wraps every framework-raised exception (AuthenticationFailed, NotFound,
    ValidationError, ParseError, etc.) in the standard error shape above,
    and logs a WARNING so every API error is visible in the container log.
    """
    response = exception_handler(exc, context)

    if response is None:
        return None

    error_type = type(exc).__name__
    data = response.data

    if isinstance(data, dict) and 'detail' in data:
        message = str(data['detail'])
    elif isinstance(data, list):
        message = '; '.join(str(item) for item in data)
    elif isinstance(data, dict):
        parts = []
        for field, errors in data.items():
            errs = errors if isinstance(errors, list) else [errors]
            parts.append(f"{field}: {', '.join(str(e) for e in errs)}")
        message = '; '.join(parts)
    else:
        message = str(data)

    response.data = {
        'error':       error_type,
        'message':     message,
        'status_code': response.status_code,
    }

    view = context.get('view')
    view_name = type(view).__name__ if view else 'unknown'
    logger.warning(
        '[%s] %s in %s: %s',
        response.status_code, error_type, view_name, message,
    )

    return response
