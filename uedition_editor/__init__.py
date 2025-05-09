# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The main uEditor server."""

import logging
from contextlib import asynccontextmanager
from copy import deepcopy

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from uvicorn.config import LOGGING_CONFIG

from uedition_editor import cron
from uedition_editor.api import router as api_router
from uedition_editor.settings import init_settings

logger = logging.getLogger(__name__)
# Configure logging
conf = deepcopy(LOGGING_CONFIG)
conf["loggers"]["uedition_editor"] = {
    "level": logging.INFO,
    "qualname": "uedition_editor",
    "handlers": ["default"],
}
conf["formatters"]["default"]["fmt"] = "%(levelprefix)s %(name)-40s %(message)s"
conf["root"] = {"level": logging.INFO}
if init_settings.test:  # pragma: no cover
    conf["loggers"]["uedition_editor"]["level"] = logging.DEBUG
logging.config.dictConfig(conf)
logger.debug("Logging configuration set up")


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa:ARG001
    """Startup/shutdown handler."""
    await cron.track_branches.func()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
app.mount("/app", StaticFiles(packages=[("uedition_editor", "frontend/dist")], html=True))


@app.get("/", response_class=RedirectResponse)
def redirect_to_app():
    """Redirect to the application UI."""
    return "/app/"
