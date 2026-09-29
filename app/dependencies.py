import secrets

from fastapi import HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .config import settings


security = HTTPBasic()


def require_admin(
    credentials: HTTPBasicCredentials
) -> None:

    if not settings.admin_password:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Admin access is not configured. "
                "Set ADMIN_PASSWORD in .env."
            ),
        )

    valid_user = secrets.compare_digest(
        credentials.username,
        settings.admin_username
    )

    valid_password = secrets.compare_digest(
        credentials.password,
        settings.admin_password
    )

    if not (valid_user and valid_password):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials.",
            headers={
                "WWW-Authenticate": "Basic"
            },
        )