# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor server API."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from pygit2 import GitError, Repository
from pygit2.enums import RepositoryOpenFlag

from uedition_editor.api.auth import router as auth_router
from uedition_editor.api.branches import router as branches_router
from uedition_editor.settings import init_settings

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(branches_router)
if init_settings.test:  # pragma: no cover
    from uedition_editor.api.tests import router as tests_router

    router.include_router(tests_router)


class APIStatusAuth(BaseModel):
    """Pydantic model for validating the auth settings."""

    provider: Literal["no-auth"] | Literal["email"] | Literal["email-password"] | Literal["github"]


class APIStatusGit(BaseModel):
    """Pydantic model for validating the git API status."""

    enabled: bool
    default_branch: str | None = None


class APIStatus(BaseModel):
    """Pydantic model for validating the API status."""

    ready: bool
    """Indicate whether the API is ready."""
    git: APIStatusGit
    """Indicate the Git status."""
    auth: APIStatusAuth
    """Indicate the authentication system status."""


@router.get("", response_model=APIStatus)
def api() -> dict:
    """Return the status of the API."""
    api_status = {
        "ready": True,
        "git": {
            "enabled": False,
        },
        "auth": {"provider": init_settings.auth.provider},
    }
    try:
        Repository(init_settings.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
        api_status["git"]["enabled"] = True
        api_status["git"]["default_branch"] = init_settings.git.default_branch
    except GitError:
        pass
    return api_status
