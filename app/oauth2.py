from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import database, models
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": str(data["user_id"]),
            "iat": now,
            "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        },
        settings.secret_key,
        algorithm="HS256",
    )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    error = HTTPException(401, "Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=["HS256"], options={"require": ["sub", "exp", "iat"]}
        )
        user = db.get(models.User, int(payload["sub"]))
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise error from None
    if user is None:
        raise error
    return user
