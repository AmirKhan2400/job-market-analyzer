from uuid import UUID, uuid4

from fastapi import Request, Response

from job_market_analyzer.config import settings

VISITOR_COOKIE_NAME = "visitor_id"


def _parse_visitor_id(value: str | None) -> str | None:
    if value is None:
        return None

    try:
        return str(UUID(value))
    except ValueError:
        return None


def get_visitor_id(request: Request, response: Response) -> str:
    existing_visitor_id = _parse_visitor_id(request.cookies.get(VISITOR_COOKIE_NAME))

    if existing_visitor_id is not None:
        return existing_visitor_id

    visitor_id = str(uuid4())
    response.set_cookie(
        key=VISITOR_COOKIE_NAME,
        value=visitor_id,
        httponly=True,
        secure=settings.visitor_cookie_secure,
        samesite=settings.visitor_cookie_samesite,
        path="/",
    )
    return visitor_id
