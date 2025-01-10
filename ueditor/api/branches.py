# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for accessing branches."""

from fastapi import APIRouter
from pydantic import BaseModel
from pygit2 import GitError, Repository
from pygit2.enums import RepositoryOpenFlag

from ueditor.api.util import uedition_lock
from ueditor.settings import init_settings

router = APIRouter(prefix="/branches")


class BranchModel(BaseModel):
    """A model of a single branch."""

    id: str
    title: str
    nogit: bool = False


def de_slugify(slug: str) -> str:
    """Turn a slug into a useable title."""
    return slug[0].capitalize() + slug[1:].replace("-", " ")


@router.get("", response_model=list[BranchModel])
async def uedition_config() -> list:
    """Fetch the available branches."""
    async with uedition_lock:
        try:
            repo = Repository(init_settings.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
            branches = []
            for branch_name in repo.branches.local:
                branches.append({"id": branch_name, "title": de_slugify(branch_name)})
            return branches
        except GitError:
            return [{"id": "-", "title": "Direct Access", "nogit": True}]
