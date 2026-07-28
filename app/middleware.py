import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth import decode_access_token
from app.database import AsyncSessionLocal
from app.models import ErrorLog


class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs all unhandled exceptions to the database and also prints the
    full traceback to the terminal for debugging.
    """

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        except Exception as exc:
            # -------------------------------
            # PRINT FULL ERROR TO TERMINAL
            # -------------------------------
            print("\n" + "=" * 80)
            print("UNHANDLED EXCEPTION")
            print("=" * 80)
            traceback.print_exc()
            print("=" * 80 + "\n")

            user_id = await self._try_get_user_id(request)
            stack_trace = "".join(
                traceback.format_exception(
                    type(exc),
                    exc,
                    exc.__traceback__,
                )
            )

            # -------------------------------
            # SAVE ERROR TO DATABASE
            # -------------------------------
            try:
                async with AsyncSessionLocal() as session:
                    session.add(
                        ErrorLog(
                            endpoint=request.url.path,
                            http_method=request.method,
                            error_message=str(exc),
                            stack_trace=stack_trace,
                            user_id=user_id,
                        )
                    )
                    await session.commit()

            except Exception as db_error:
                print("\nFailed to save error log")
                traceback.print_exception(
                    type(db_error),
                    db_error,
                    db_error.__traceback__,
                )

            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "detail": "An unexpected error occurred. Check the server console.",
                },
            )

    @staticmethod
    async def _try_get_user_id(request: Request):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.removeprefix("Bearer ").strip()

        try:
            return decode_access_token(token)
        except Exception:
            return None