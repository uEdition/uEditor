# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for accessing branches."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field
from pygit2 import GitError, Repository, Signature
from pygit2.enums import RepositoryOpenFlag

from uedition_editor import cron
from uedition_editor.api.auth import get_current_user
from uedition_editor.api.configs import router as configs_router
from uedition_editor.api.files import router as files_router
from uedition_editor.api.util import (
    BranchContextManager,
    RemoteRepositoryCallbacks,
    commit_and_push,
    de_slugify,
    fetch_and_pull_branch,
    fetch_repo,
    pull_branch,
    slugify,
    uedition_lock,
)
from uedition_editor.settings import init_settings
from uedition_editor.state import local_branches, remote_branches

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/branches")
router.include_router(files_router, prefix="/{branch_id}")
router.include_router(configs_router, prefix="/{branch_id}")


class BranchModel(BaseModel):
    """A model of a single branch."""

    id: str
    title: str
    nogit: bool = False
    update_from_default: bool = False


class BranchesModel(BaseModel):
    """A model combining local and remote branches."""

    local: list[BranchModel]
    remote: list[BranchModel]


@router.get("", response_model=BranchesModel)
async def branches(
    current_user: Annotated[dict, Depends(get_current_user)],  # noqa:ARG001
) -> list:
    """Fetch the available branches."""
    return {"local": local_branches, "remote": remote_branches}


@router.patch("", status_code=204)
async def synchronise_remote() -> None:
    """Synchronise with the git remote."""
    await cron.track_branches.func()


class CreateBranchModel(BaseModel):
    """Model representing a new branch."""

    title: str = Field(min_length=1)


@router.post("", response_model=BranchModel)
async def create_branch(
    data: CreateBranchModel,
    current_user: Annotated[dict, Depends(get_current_user)],  # noqa:ARG001
    x_ueditor_import_branch: Annotated[bool, Header()] = False,  # noqa: FBT002
) -> dict:
    """Create a new branch."""
    async with uedition_lock:
        try:
            branch_id = slugify(data.title)
            repo = Repository(init_settings.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
            if branch_id in repo.branches.local:
                raise HTTPException(422, detail=[{"msg": "this branch name is already in use"}])
            if init_settings.git.remote_name in list(repo.remotes.names()):
                fetch_and_pull_branch(
                    repo,
                    init_settings.git.remote_name,
                    init_settings.git.default_branch,
                )
            repo.checkout(repo.branches[init_settings.git.default_branch])
            if x_ueditor_import_branch:
                commit, reference = repo.resolve_refish(f"{init_settings.git.remote_name}/{branch_id}")
                repo.branches.local.create(branch_id, commit)
                repo.checkout(repo.branches[branch_id])
                repo.branches[branch_id].upstream = repo.branches[f"{init_settings.git.remote_name}/{branch_id}"]
                await cron.insecure_track_branches()
                return {"id": branch_id, "title": de_slugify(data.title)}
            else:
                for remote_branch_id in repo.branches.remote:
                    if remote_branch_id.endswith(branch_id):
                        raise HTTPException(
                            422,
                            detail=[{"msg": "this branch name is already used in the remote repository"}],
                        )
                last_default_commit = repo.revparse_single(str(repo.branches[init_settings.git.default_branch].target))
                repo.branches.local.create(branch_id, last_default_commit)
                repo.checkout(repo.branches[branch_id])
                if init_settings.git.remote_name in list(repo.remotes.names()):
                    repo.remotes[init_settings.git.remote_name].push(
                        [f"refs/heads/{branch_id}"],
                        callbacks=RemoteRepositoryCallbacks(),
                    )
                    fetch_repo(repo, init_settings.git.remote_name)
                    repo.branches[branch_id].upstream = repo.branches[f"{init_settings.git.remote_name}/{branch_id}"]
                await cron.insecure_track_branches()
                return {"id": branch_id, "title": data.title}
        except GitError as ge:
            logger.error(ge)
            raise HTTPException(500, "Git error") from ge


@router.post("/{branch_id}/merge-from-default", status_code=204)
async def merge_from_default(
    branch_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> None:
    """Merge all changes from the default branch."""
    async with BranchContextManager(branch_id) as repo:
        repo.checkout(repo.branches[init_settings.git.default_branch])
        if init_settings.git.remote_name in list(repo.remotes.names()):
            fetch_repo(repo, init_settings.git.remote_name)
            pull_branch(repo, init_settings.git.default_branch)
        repo.checkout(repo.branches[branch_id])
        default_branch_head = repo.revparse_single(init_settings.git.default_branch)
        diff = repo.diff(default_branch_head)
        if diff.stats.files_changed > 0:
            repo.merge(default_branch_head.id)
            commit_and_push(
                repo,
                init_settings.git.remote_name,
                branch_id,
                f"Merged {init_settings.git.default_branch}",
                Signature(current_user["name"], current_user["sub"]),
                extra_parents=[default_branch_head.id],
            )


@router.delete("/{branch_id}", status_code=204)
async def delete_branch(
    branch_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],  # noqa:ARG001
) -> None:
    """Delete the given branch locally and remotely."""
    async with BranchContextManager(branch_id) as repo:
        fetch_and_pull_branch(repo, init_settings.git.remote_name, branch_id)
        if init_settings.git.default_branch == branch_id:
            raise HTTPException(422, detail=[{"msg": "you cannot delete the default branch"}])
        repo.checkout(repo.branches[init_settings.git.default_branch])
        if init_settings.git.remote_name in list(repo.remotes.names()):
            if repo.branches[branch_id].upstream is not None:
                repo.remotes[init_settings.git.remote_name].push(
                    [f":refs/heads/{branch_id}"], callbacks=RemoteRepositoryCallbacks()
                )
        if branch_id in repo.branches:
            repo.branches.delete(branch_id)
        await cron.insecure_track_branches()
