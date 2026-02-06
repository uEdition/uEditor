# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor CLI application."""

import re
from typing import Annotated

from pygit2 import GitError, Repository, Signature, init_repository
from pygit2.enums import RepositoryOpenFlag
from rich import print  # noqa:A004
from typer import Context, Option, Typer
from uvicorn import Config, Server

from uedition_editor.__about__ import __version__
from uedition_editor.api.util import RemoteRepositoryCallbacks
from uedition_editor.settings import init_settings

app = Typer()
git_app = Typer(help="Git configuration functionality")
app.add_typer(git_app, name="git")


@app.command()
def version() -> None:
    """Output the μEditor version."""
    print(__version__)


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def server(ctx: Context) -> None:
    """Run the μEditor server."""
    settings = {"port": 8000}
    key = None
    for arg in ctx.args:
        if arg.startswith("--"):
            key = arg[2:]
        elif key is not None:
            if re.match("[0-9]+", arg):
                settings[key] = int(arg)
            else:
                settings[key] = arg
            key = None
    config = Config("uedition_editor:app", **settings)
    server = Server(config)
    server.run()


@git_app.command()
def init(name: Annotated[str, Option(prompt="Name")], email: Annotated[str, Option(prompt="E-Mail address")]):
    """Initialise the git repository."""
    try:
        Repository(init_settings.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
        print("[red]This μEdition already has a git repository set up[/red]")
        return
    except GitError:
        pass
    with open(".env", "w") as out_f:
        out_f.write(f"""UEDITOR__AUTH__PROVIDER=email
UEDITOR__AUTH__NAME={name}
UEDITOR__AUTH__EMAIL={email}
UEDITOR__GIT__DEFAULT_BRANCH=main
""")
    with open(".gitignore", "w") as out_f:
        out_f.write("""_build
site
_toc.yml
conf.py
""")
    repo = init_repository(init_settings.base_path)
    index = repo.index
    index.add_all()
    index.write()
    tree = index.write_tree()
    repo.create_commit("HEAD", Signature(name, email), Signature(name, email), "Initial state", tree, [])
    commit, _ = repo.resolve_refish("HEAD")
    repo.branches.local.create(init_settings.git.default_branch, commit)
    repo.checkout(repo.branches.local[init_settings.git.default_branch])
    for branch_name in repo.branches.local:
        if branch_name != init_settings.git.default_branch:
            repo.branches.local.delete(branch_name)


@git_app.command()
def set_remote(url: Annotated[str, Option(prompt="Git URL")]):
    """Set the remote URL."""
    repo = Repository(init_settings.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
    for remote in repo.remotes:
        if remote.name == init_settings.git.remote_name:
            repo.remotes.delete(init_settings.git.remote_name)
    repo.remotes.create(init_settings.git.remote_name, url)
    repo.remotes[init_settings.git.remote_name].push(
        [f"refs/heads/{init_settings.git.default_branch}"], callbacks=RemoteRepositoryCallbacks()
    )
    repo.branches[init_settings.git.default_branch].upstream = repo.branches[
        f"{init_settings.git.remote_name}/{init_settings.git.default_branch}"
    ]
