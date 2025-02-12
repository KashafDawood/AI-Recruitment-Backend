from django.conf import settings
import datetime
from datetime import UTC


def set_http_only_cookie(res, access_token, refresh):
    # set acess token cookie
    res.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=access_token,
        httponly=True,
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        expires=datetime.datetime.now(UTC)
        + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
    )

    # Set Refresh Token Cookie
    res.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
        value=str(refresh),
        httponly=True,
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        expires=datetime.datetime.now(UTC)
        + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
    )
