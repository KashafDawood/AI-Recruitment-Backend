from django.conf import settings
import datetime
from datetime import UTC


def set_http_only_cookie(res, access_token, refresh):
    # Set access token cookie
    res.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=access_token,
        httponly=True,
        secure=True,  # Ensure secure attribute is set to True
        samesite="None",  # Updated SameSite attribute
        expires=datetime.datetime.now(UTC)
        + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
    )

    # Set refresh token cookie
    res.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
        value=str(refresh),
        httponly=True,
        secure=True,  # Ensure secure attribute is set to True
        samesite="None",  # Updated SameSite attribute
        expires=datetime.datetime.now(UTC)
        + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
    )

    return res
