from django.conf import settings
import datetime
from datetime import UTC


def set_http_only_cookie(res, access_token, refresh):
    # Common cookie settings
    cookie_settings = {
        "httponly": True,
        "secure": True,  # Required for SameSite=None
        "samesite": "None",
        "domain": settings.SIMPLE_JWT.get("AUTH_COOKIE_DOMAIN"),
        "path": settings.SIMPLE_JWT.get("AUTH_COOKIE_PATH", "/"),
    }

    # Set access token cookie
    res.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=access_token,
        expires=datetime.datetime.now(UTC)
        + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        **cookie_settings
    )

    # Set refresh token cookie
    res.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
        value=str(refresh),
        expires=datetime.datetime.now(UTC)
        + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
        **cookie_settings
    )
