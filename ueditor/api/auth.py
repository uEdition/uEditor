"""Authentication functionality."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Cookie, Depends, Response
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, EmailStr

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
                options={"require": ["exp", "iat", "name", "nbf", "provider", "sub"]},
            )
            if init_settings.auth.provider in ["no-auth", "email"]:
                if data["sub"] != init_settings.auth.email or data["provider"] != init_settings.auth.provider:
                    raise HTTPException(401)
            elif init_settings.auth.provider == "email-password":
                if data["provider"] != init_settings.auth.provider:
                    raise HTTPException(401)
                for user in init_settings.auth.users:
                    if data["sub"] == user.email:
                        return data
                raise HTTPException(401)
            return data
        except jwt.InvalidTokenError as e:
            logger.error(e)
            raise HTTPException(401) from e
    raise HTTPException(401)


class EmailPasswordLoginModel(BaseModel):
    """Model for validating login via email and password."""

    email: EmailStr
    password: str


@router.post("/login", status_code=204)
def login(response: Response, auth: EmailPasswordLoginModel | None = None) -> None:
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
                "provider": init_settings.auth.provider,
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
    elif init_settings.auth.provider == "email-password" and auth is not None:
        for user in init_settings.auth.users:
            if user.email == auth.email and user.password == auth.password:
                now = datetime.now(timezone.utc)
                ueditor_user = jwt.encode(
                    {
                        "sub": user.email,
                        "name": user.name,
                        "exp": now + timedelta(days=14),
                        "iat": now,
                        "nbf": now,
                        "provider": init_settings.auth.provider,
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
