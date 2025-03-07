# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor CLI application."""

import re

from typer import Context, Typer
from uvicorn import Config, Server

from uedition_editor.__about__ import __version__

app = Typer()


@app.command()
def version() -> None:
    """Output the μEditor version."""
    print(__version__)  # noqa:T201


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
