# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor server API."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from pygit2 import GitError, Repository
from pygit2.enums import RepositoryOpenFlag

from ueditor.api.auth import router as auth_router
from ueditor.api.branches import router as branches_router
from ueditor.settings import init_settings

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(branches_router)
if init_settings.test:  # pragma: no cover
    from ueditor.api.tests import router as tests_router

    router.include_router(tests_router)


class APIStatusAuth(BaseModel):
    """Pydantic model for validating the auth settings."""

    provider: Literal["no-auth"] | Literal["email"] | Literal["email-password"]


class APIStatus(BaseModel):
    """Pydantic model for validating the API status."""

    ready: bool
    """Indicate whether the API is ready."""
    git_enabled: bool
    """Indicate whether Git is available."""
    auth: APIStatusAuth


@router.get("", response_model=APIStatus)
def api() -> dict:
    """Return the status of the API."""
    api_status = {
        "ready": True,
        "git_enabled": False,
        "auth": {"provider": init_settings.auth.provider},
    }
    try:
        Repository(init_settings.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
        api_status["git_enabled"] = True
    except GitError:
        pass
    return api_status
