"""Authentication functionality."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Cookie, Depends, Response
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from ueditor.settings import init_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth")


def current_user(ueditor_user: Annotated[str | None, Cookie()] = None):
    """Get the current user from the session cookie."""
    if ueditor_user is not None:
        try:
            data = jwt.decode(
                ueditor_user,
                key=init_settings.session.key,
                algorithms="HS512",
                options={"require": ["exp", "iat", "name", "nbf", "sub"]},
            )
            if init_settings.auth.provider in ["no-auth", "email", "email-password"]:
                if data["sub"] != init_settings.auth.email:
                    raise HTTPException(401)
            return data
        except jwt.InvalidTokenError as e:
            logger.error(e)
            raise HTTPException(401) from e
    raise HTTPException(401)


@router.post("/login", status_code=204)
def login(response: Response) -> None:
    """Log the user in using one of the local authentication methods."""
    if init_settings.auth.provider in ["no-auth", "email"]:
        now = datetime.now(timezone.utc)
        ueditor_user = jwt.encode(
            {
                "sub": init_settings.auth.email,
                "name": init_settings.auth.name,
                "exp": now + timedelta(days=14),
                "iat": now,
                "nbf": now,
            },
            init_settings.session.key,
            algorithm="HS512",
        )
        response.set_cookie(
            "ueditor_user",
            ueditor_user,
            expires=now + timedelta(14),
            secure=True,
            samesite="strict",
        )
        return
    raise HTTPException(403)


@router.delete("/login", status_code=204)
def logout(response: Response) -> None:
    """Log the user out."""
    response.delete_cookie(
        "ueditor_user",
        secure=True,
        samesite="strict",
    )


class UserModel(BaseModel):
    """Pydantic model for validating user responses."""

    sub: str
    name: str


@router.get("/user", response_model=UserModel)
def user(current_user: Annotated[dict, Depends(current_user)]):
    """Return the currently logged in user."""
    return current_user
