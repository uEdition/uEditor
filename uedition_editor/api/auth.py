"""Authentication functionality."""

import logging
from datetime import datetime, timedelta, timezone
from secrets import token_hex
from typing import Annotated
from urllib.parse import urlencode

import jwt
from fastapi import APIRouter, Cookie, Depends, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from httpx import AsyncClient
from pydantic import BaseModel, EmailStr

from uedition_editor.settings import init_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth")


def get_current_user(ueditor_user: Annotated[str | None, Cookie()] = None):
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


OIDC_STATES = {}


@router.get("/oidc/login", response_class=RedirectResponse)
def start_oidc_login():
    """Start an OIDC (or equivalent) authorization process."""
    if init_settings.auth.provider != "github":
        raise HTTPException(404)
    state = token_hex(64)
    now = datetime.now(tz=timezone.utc).timestamp()
    valid_until = now + 600
    OIDC_STATES[state] = valid_until
    for key in list(OIDC_STATES.keys()):
        if now > OIDC_STATES[key]:
            del OIDC_STATES[key]
    params = {
        "client_id": init_settings.auth.client_id,
        "redirect_uri": f"{init_settings.auth.callback_base}/api/auth/oidc/callback",
        "scope": "read:user",
        "state": state,
    }
    return f"https://github.com/login/oauth/authorize?{urlencode(params)}"


@router.get("/oidc/callback", response_class=RedirectResponse)
async def complete_oidc_login(code: str, state: str, redirect_response: Response):
    """Complete an OIDC (or equivalent) authorization process."""
    if init_settings.auth.provider != "github":
        raise HTTPException(404)
    now = datetime.now(tz=timezone.utc)
    if state not in OIDC_STATES or now.timestamp() > OIDC_STATES[state]:
        raise HTTPException(403)
    async with AsyncClient() as client:
        params = {
            "client_id": init_settings.auth.client_id,
            "client_secret": init_settings.auth.client_secret,
            "code": code,
            "redirect_uri": f"{init_settings.auth.callback_base}/api/auth/oidc/callback",
        }
        response = await client.get(
            f"https://github.com/login/oauth/access_token?{urlencode(params)}",
            headers={"Accept": "application/json"},
        )
        if response.status_code != 200:  # noqa:PLR2004
            raise HTTPException(403)
        token = response.json()
        response = await client.get(
            "https://api.github.com/user",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token['access_token']}",
            },
        )
        if response.status_code != 200:  # noqa: PLR2004
            raise HTTPException(403)
        user_data = response.json()
        if user_data["email"] not in init_settings.auth.users:
            raise HTTPException(403)
        ueditor_user = jwt.encode(
            {
                "sub": user_data["email"],
                "name": user_data["name"],
                "exp": now + timedelta(days=14),
                "iat": now,
                "nbf": now,
                "provider": init_settings.auth.provider,
            },
            init_settings.session.key,
            algorithm="HS512",
        )
        redirect_response.set_cookie(
            "ueditor_user",
            ueditor_user,
            expires=now + timedelta(14),
            secure=True,
            samesite="strict",
        )
        return "/app"


class UserModel(BaseModel):
    """Pydantic model for validating user responses."""

    sub: str
    name: str


@router.get("/user", response_model=UserModel)
def user(current_user: Annotated[dict, Depends(get_current_user)]):
    """Return the currently logged in user."""
    return current_user
