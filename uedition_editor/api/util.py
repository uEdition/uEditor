"""Utility functionality for the API."""

import logging
from asyncio import Lock

from pygit2 import (
    CredentialType,
    GitError,
    KeypairFromAgent,
    RemoteCallbacks,
    Repository,
    Signature,
)
from pygit2.enums import FetchPrune, MergeAnalysis, RepositoryOpenFlag

from uedition_editor.settings import init_settings

logger = logging.getLogger(__name__)
uedition_lock = Lock()


class BranchNotFoundError(BaseException):
    """Error indicating that a branch was not found."""

    pass


class BranchContextManager:
    """An async ContextManager that checks out the appropriate branch."""

    def __init__(self, branch_id: str):
        """Initialise the context manager."""
        self._branch_id = branch_id
        try:
            self._repo = Repository(init_settings.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
        except GitError:
            self._repo = None

    async def __aenter__(self) -> Repository | None:
        """Enter the context manager, acquiring the lock and checking out the correct branch."""
        await uedition_lock.acquire()
        if self._repo:
            branch = self._repo.lookup_branch(self._branch_id)
            if branch is not None:
                self._repo.checkout(branch)
            else:
                uedition_lock.release()
                raise BranchNotFoundError
        return self._repo

    async def __aexit__(self, exc_type, exc, tb):
        """Exit the context manager, releasing the lock."""
        uedition_lock.release()


class RemoteRepositoryCallbacks(RemoteCallbacks):
    """Callback handler for connecting to remote repositories."""

    def credentials(
        self,
        url: str,  # noqa: ARG002
        username_from_url: str | None,
        allowed_types: CredentialType,
    ):
        """Return the credentials for the remote connection."""
        if allowed_types & CredentialType.SSH_KEY == CredentialType.SSH_KEY:
            return KeypairFromAgent(username_from_url)
        else:
            return None


def fetch_repo(repo: Repository, remote: str) -> None:
    """Fetch the remote repository."""
    repo.remotes[remote].fetch(prune=FetchPrune.PRUNE, callbacks=RemoteRepositoryCallbacks())


def pull_branch(repo: Repository, branch: str) -> None:
    """Pull and update the branch from the remote repository."""
    try:
        remote_default_head = repo.lookup_reference(repo.branches[branch].upstream_name)
        result, _ = repo.merge_analysis(remote_default_head.target)
        if result & MergeAnalysis.FASTFORWARD == MergeAnalysis.FASTFORWARD:
            repo.checkout_tree(repo.get(remote_default_head.target))
            local_default_head = repo.lookup_reference(f"refs/heads/{branch}")
            local_default_head.set_target(remote_default_head.target)
            repo.head.set_target(remote_default_head.target)
    except KeyError as e:
        logger.error(e)


def fetch_and_pull_branch(repo: Repository, remote: str, branch: str) -> None:
    """Fetch and pull the `branch` from the `remote` repository."""
    repo.checkout(repo.branches[branch])
    fetch_repo(repo, remote)
    pull_branch(repo, branch)


def commit_and_push(
    repo: Repository,
    remote: str,
    branch: str,
    commit_msg: str,
    author: Signature,
    extra_parents: list[str] | None = None,
) -> None:
    """Commit changes to the repository and push."""
    if len(repo.status()) > 0:
        logger.debug(f"Committing changes to {', '.join(repo.status().keys())}")
        ref = repo.head.name
        parents = [repo.head.target]
        if extra_parents is not None:
            parents.extend(extra_parents)
        index = repo.index
        index.add_all()
        index.write()
        tree = index.write_tree()
        repo.create_commit(ref, author, author, commit_msg, tree, parents)
        if remote in repo.remotes.names():
            logger.debug(f"Pushing changes to {remote}")
            repo.remotes[remote].push([f"refs/heads/{branch}"], callbacks=RemoteRepositoryCallbacks())


def slugify(slug: str) -> str:
    """Turn a title into a slug."""
    return slug.lower().replace(" ", "-")


def de_slugify(slug: str) -> str:
    """Turn a slug into a useable title."""
    return slug[0].capitalize() + slug[1:].replace("-", " ")
