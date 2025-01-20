"""Utility functionality for the API."""

from asyncio import Lock

from pygit2 import GitError, Repository
from pygit2.enums import RepositoryOpenFlag

from ueditor.settings import init_settings

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
