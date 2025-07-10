# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Regular jobs run in the background of the uEditor."""

import logging

import aiocron
from pygit2 import GitError, Repository
from pygit2.enums import RepositoryOpenFlag

from uedition_editor.api.util import de_slugify, fetch_repo, pull_branch, uedition_lock
from uedition_editor.settings import init_settings
from uedition_editor.state import local_branches, remote_branches

logger = logging.getLogger(__name__)


async def insecure_track_branches():
    """
    Track the status of all git branches.

    Use only when the uedition_lock is already completed.
    """
    remote_branches.clear()
    local_branches.clear()
    try:
        repo = Repository(init_settings.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
        logger.debug("Tracking branches")
        repo.checkout(repo.branches[init_settings.git.default_branch])
        if init_settings.git.remote_name in list(repo.remotes.names()):
            logger.debug("Synchronising with remote")
            fetch_repo(repo, init_settings.git.remote_name)
        logger.debug("Updating branch status")
        for branch_name in repo.branches.local:
            repo.checkout(repo.branches[branch_name])
            if init_settings.git.remote_name in list(repo.remotes.names()):
                if repo.branches[branch_name].upstream is not None:
                    pull_branch(repo, branch_name)
            diff = repo.diff(
                repo.revparse_single(init_settings.git.default_branch),
            )
            local_branches.append(
                {
                    "id": branch_name,
                    "title": de_slugify(branch_name),
                    "update_from_default": diff.stats.files_changed > 0,
                }
            )
        for branch_name in repo.branches.remote:
            if repo.branches[branch_name].remote_name == init_settings.git.remote_name and "HEAD" not in branch_name:
                remote_branches.append({"id": branch_name, "title": de_slugify(branch_name)})
        logger.debug("Tracking complete")
    except GitError as ge:
        logger.error(ge)
        local_branches.append({"id": "-", "title": "Direct Access", "nogit": True})


@aiocron.crontab("*/5 * * * *")
async def track_branches() -> None:
    """Track the status of all git branches."""
    async with uedition_lock:
        await insecure_track_branches()
