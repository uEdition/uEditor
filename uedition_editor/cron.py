# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Regular jobs run in the background of the uEditor."""

import logging

import aiocron
from pygit2 import GitError, Repository
from pygit2.enums import RepositoryOpenFlag

from uedition_editor.api.util import fetch_repo, pull_branch, uedition_lock
from uedition_editor.settings import init_settings

logger = logging.getLogger(__name__)


@aiocron.crontab("* * * * *")
async def sync_remote() -> None:
    """Synchronise with the remote."""
    async with uedition_lock:
        try:
            repo = Repository(init_settings.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
            repo.checkout(repo.branches[init_settings.git.default_branch])
            if init_settings.git.remote_name in list(repo.remotes.names()):
                logging.debug("Synchronising with remote")
                fetch_repo(repo, init_settings.git.remote_name)
                for branch_id in repo.branches.local:
                    if repo.branches[branch_id].upstream is not None:
                        pull_branch(repo, branch_id)
        except GitError as ge:
            logger.error(ge)
