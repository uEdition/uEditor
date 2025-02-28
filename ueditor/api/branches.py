# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for accessing branches."""

import logging
from typing import Annotated

from fastapi import APIRouter, Header
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field
from pygit2 import GitError, Repository
from pygit2.enums import FetchPrune, RepositoryOpenFlag

from ueditor.api.configs import router as configs_router
from ueditor.api.files import router as files_router
from ueditor.api.util import (
    BranchContextManager,
    RemoteRepositoryCallbacks,
    fetch_and_pull_branch,
    fetch_repo,
    pull_branch,
    uedition_lock,
)
from ueditor.settings import get_ueditor_settings, init_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/branches")
router.include_router(files_router, prefix="/{branch_id}")
router.include_router(configs_router, prefix="/{branch_id}")


class BranchModel(BaseModel):
    """A model of a single branch."""

    id: str
    title: str
    nogit: bool = False


def slugify(slug: str) -> str:
    """Turn a title into a slug."""
    return slug.lower().replace(" ", "-")


def de_slugify(slug: str) -> str:
    """Turn a slug into a useable title."""
    return slug[0].capitalize() + slug[1:].replace("-", " ")


@router.get("", response_model=list[BranchModel])
async def branches(category: str = "local") -> list:
    """Fetch the available branches."""
    if category not in ("local", "remote"):
        raise HTTPException(404, "No such branch category found")
    async with uedition_lock:
        try:
            repo = Repository(init_settings.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
            branches = []
            if category == "local":
                for branch_name in repo.branches.local:
                    branches.append({"id": branch_name, "title": de_slugify(branch_name)})
            elif category == "remote":
                settings = get_ueditor_settings()
                if settings.git.remote_name in list(repo.remotes.names()):
                    repo.remotes[settings.git.remote_name].fetch(
                        prune=FetchPrune.PRUNE, callbacks=RemoteRepositoryCallbacks()
                    )
                    for branch_name in repo.branches.remote:
                        if (
                            repo.branches[branch_name].remote_name == settings.git.remote_name
                            and "HEAD" not in branch_name
                        ):
                            branches.append({"id": branch_name, "title": de_slugify(branch_name)})
            return branches
        except GitError as ge:
            logger.error(ge)
            if category == "local":
                return [{"id": "-", "title": "Direct Access", "nogit": True}]
            elif category == "remote":
                return []


class CreateBranchModel(BaseModel):
    """Model representing a new branch."""

    title: str = Field(min_length=1)


@router.post("", response_model=BranchModel)
async def create_branch(
    data: CreateBranchModel,
    x_ueditor_import_branch: Annotated[bool, Header()] = False,  # noqa: FBT002
) -> dict:
    """Create a new branch."""
    async with uedition_lock:
        try:
            branch_id = slugify(data.title)
            repo = Repository(init_settings.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
            if branch_id in repo.branches.local:
                raise HTTPException(422, detail=[{"msg": "this branch name is already in use"}])
            settings = get_ueditor_settings()
            if settings.git.remote_name in list(repo.remotes.names()):
                fetch_and_pull_branch(repo, settings.git.remote_name, settings.git.default_branch)
            repo.checkout(repo.branches[settings.git.default_branch])
            if x_ueditor_import_branch:
                commit, reference = repo.resolve_refish(f"{settings.git.remote_name}/{branch_id}")
                repo.branches.local.create(branch_id, commit)
                repo.checkout(repo.branches[branch_id])
                repo.branches[branch_id].upstream = repo.branches[f"{settings.git.remote_name}/{branch_id}"]
                return {"id": branch_id, "title": de_slugify(data.title)}
            else:
                for remote_branch_id in repo.branches.remote:
                    if remote_branch_id.endswith(branch_id):
                        raise HTTPException(
                            422, detail=[{"msg": "this branch name is already used in the remote repository"}]
                        )
                last_default_commit = repo.revparse_single(str(repo.branches[settings.git.default_branch].target))
                repo.branches.local.create(branch_id, last_default_commit)
                repo.checkout(repo.branches[branch_id])
                if settings.git.remote_name in list(repo.remotes.names()):
                    repo.remotes[settings.git.remote_name].push(
                        [f"refs/heads/{branch_id}"], callbacks=RemoteRepositoryCallbacks()
                    )
                    fetch_repo(repo, settings.git.remote_name)
                    repo.branches[branch_id].upstream = repo.branches[f"{settings.git.remote_name}/{branch_id}"]
                return {"id": branch_id, "title": data.title}
        except GitError as ge:
            logger.error(ge)
            raise HTTPException(500, "Git error") from ge


@router.patch("", status_code=204)
async def fetch_branches() -> None:
    """Update the branches from the remote."""
    async with uedition_lock:
        try:
            repo = Repository(init_settings.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
            settings = get_ueditor_settings()
            repo.checkout(repo.branches[settings.git.default_branch])
            settings = get_ueditor_settings()
            if settings.git.remote_name in list(repo.remotes.names()):
                fetch_repo(repo, settings.git.remote_name)
                for branch_id in repo.branches.local:
                    if repo.branches[branch_id].upstream is not None:
                        pull_branch(repo, branch_id)
        except GitError as ge:
            logger.error(ge)
            raise HTTPException(500, "Git error") from ge


@router.delete("/{branch_id}", status_code=204)
async def delete_branch(branch_id: str) -> None:
    """Delete the given branch locally and remotely."""
    async with BranchContextManager(branch_id) as repo:
        settings = get_ueditor_settings()
        fetch_and_pull_branch(repo, settings.git.remote_name, branch_id)
        settings = get_ueditor_settings()
        if settings.git.default_branch == branch_id:
            raise HTTPException(422, detail=[{"msg": "you cannot delete the default branch"}])
        repo.checkout(repo.branches[settings.git.default_branch])
        settings = get_ueditor_settings()
        if settings.git.remote_name in list(repo.remotes.names()):
            if repo.branches[branch_id].upstream is not None:
                repo.remotes[settings.git.remote_name].push(
                    [f":refs/heads/{branch_id}"], callbacks=RemoteRepositoryCallbacks()
                )
        if branch_id in repo.branches:
            repo.branches.delete(branch_id)
