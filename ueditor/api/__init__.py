# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor server API."""

from fastapi import APIRouter
from pydantic import BaseModel
from pygit2 import GitError, Repository
from pygit2.enums import RepositoryOpenFlag

from ueditor.api.branches import router as branches_router
from ueditor.api.files import router as files_router
from ueditor.settings import init_settings

router = APIRouter(prefix="/api")
router.include_router(branches_router)
router.include_router(files_router)
if init_settings.test:  # pragma: no cover
    from ueditor.api.tests import router as tests_router

    router.include_router(tests_router)


class APIStatus(BaseModel):
    """Pydantic model for validating the API status."""

    ready: bool
    """Indicate whether the API is ready."""
    git_enabled: bool
    """Indicate whether Git is available."""


@router.get("", response_model=APIStatus)
def api() -> dict:
    """Return the status of the API."""
    git_enabled = False
    try:
        Repository(init_settings.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
        git_enabled = True
    except GitError:
        pass
    return {"ready": True, "git_enabled": git_enabled}
