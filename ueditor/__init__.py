# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The main uEditor server."""

import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from ueditor.api import router as api_router
from ueditor.settings import init_settings

if init_settings.test:  # pragma: no cover
    logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
app.include_router(api_router)
app.mount("/app", StaticFiles(packages=[("ueditor", "frontend/dist")], html=True))


@app.get("/", response_class=RedirectResponse)
def redirect_to_app():
    """Redirect to the application UI."""
    return "/app/"
